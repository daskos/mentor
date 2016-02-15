from mesos.interface import mesos_pb2


class StatusUpdateHandler(object):
    modifiers = {
        mesos_pb2.TASK_RUNNING: [('running', 1)],
        mesos_pb2.TASK_FINISHED: [('running', -1), ('successful', 1)],
        mesos_pb2.TASK_FAILED: [('running', -1), ('failed', 1)],
        mesos_pb2.TASK_LOST: [('running', -1), ('failed', 1)],
        mesos_pb2.TASK_KILLED: [('running', -1), ('failed', 1)],
        mesos_pb2.TASK_STAGING: [],
        mesos_pb2.TASK_STARTING: []
    }

    def __init__(self, scheduler):
        self.scheduler = scheduler

    def __call__(self, scheduler, driver, taskStatus):
        status = taskStatus.state
        print 'Recieved a status update [%s]' % status
        if status not in self.modifiers:
            print 'Unknown state code [%s]' % status

        for name, value in self.modifiers[status]:
            self.scheduler.task_stats[name] += value

        self.scheduler.driver_states['is_starting'] = False

        # TODO do something w/ this extreme code smell
        if self.scheduler.satyr:
            self.scheduler.satyr.update_task_status(taskStatus)
