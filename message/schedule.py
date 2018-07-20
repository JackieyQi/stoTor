#! /usr/bin/env python
# coding: utf8
# @Time: 18-01-06
# @Author: yyq

from apscheduler.schedulers.tornado import TornadoScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from config import CFG
# from config import SCHEDULE_JOBSTORES_URL, EXECUTOR_POOL_THREADS, EXECUTOR_POOL_PROCESSES

class SScheduler(object):
    def __init__(self, logger=None):
        jobstores = {"mysql": SQLAlchemyJobStore(url=CFG.SCHEDULE_JOBSTORES_URL)}
        executors = {"default": ThreadPoolExecutor(CFG.EXECUTOR_POOL_THREADS),
                     "processpool": ProcessPoolExecutor(CFG.EXECUTOR_POOL_PROCESSES)}
        job_defaults = {'coalesce': False, 'max_instances': 3}

        self.logger = logger
        self.scheduler = TornadoScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)
        self.scheduler.start()
        self.init_listener()

    def init_listener(self):
        self.scheduler.add_listener(self.listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    def listener(self, event):
        if event.exception:
            print("job exception")
            # log
        else:
            print("job over")

    def init_main_job(self):
        from data.sto_code import init_sto_data
        self.scheduler.add_job(init_sto_data, "cron", day_of_week="mon-fri", hour=8)

        # 每日成交额更新
        from data.sto_code import save_sto_turnover
        self.scheduler.add_job(save_sto_turnover, "cron", day_of_week="mon-fri", hour=19)

        # 每日持股数值更新
        from data.capital_flow.market_cap import save_daily_market_cap
        self.scheduler.add_job(save_daily_market_cap, "cron", day_of_week="tue-sat", hour=9)

        self.init_real_job()

    def init_real_job(self):
        from data.real_quotes.mind import save_k_data, clear_k_data
        self.scheduler.add_job(save_k_data, "cron", day_of_week="mon-fri", hour="9-14", minute="*/3")

        self.scheduler.add_job(clear_k_data, "cron", day_of_week="mon-fri", hour="20")

