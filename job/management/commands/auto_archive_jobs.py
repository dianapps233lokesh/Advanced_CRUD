
from django.core.management.base import BaseCommand
from datetime import timedelta
from django.utils import  timezone
from job.models import Job
import pytz

class Command(BaseCommand):
    help='this automatically archives jobs that are created 30 days before and whose milestones are approved and completed'

    def handle(self, *args, **options):
        cutoff=timezone.now()-timedelta(days=1)
        ist = pytz.timezone("Asia/Kolkata")
        cutoff_ist = cutoff.astimezone(ist)
        print("cutoff before",cutoff)
        print("cutoff after",cutoff_ist)
        jobs=Job.objects.filter(is_archived=False,created_at__lt=cutoff_ist)
        archived_count=0
        for job in jobs:
            milestones=job.milestones.all()
            print(milestones)

            # for m in milestones:
            #     print(m.is_completed_by_freelancer,m.is_approved_by_employer)
            if milestones.exists() and all(m.is_completed_by_freelancer and m.is_approved_by_employer for m in milestones):
                # print("hii we have passed all condition")
                job.is_archived=True
                job.save()
                archived_count+=1
                print(f"archived job {job.id} and {job.title}")
        print("total archived jobs:",archived_count)
