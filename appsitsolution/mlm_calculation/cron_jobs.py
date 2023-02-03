from datetime import date

from django_cron import CronJobBase, Schedule

from .pgpv_pgbv import do_pgpv_pgbv_calculation

class PgpvPgbvDailyUpdate(CronJobBase):
    RUN_AT_TIMES = ['00:05']

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'mlm_calculation.pgpv_pgbv_daily_updates'    # a unique code

    def do(self):
        today_date = date.today()
        month_cal = '{}-{}'.format(today_date.year, today_date.month)
        do_pgpv_pgbv_calculation(month_cal)
