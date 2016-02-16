from mesos.interface import mesos_pb2


"""Put all the horrible mesos protobuf instantiations
into this equally horrible collection of factories. I'm
almost certain that there's a better way to do this."""
def build(name, *args, **kwargs):
    def executor_info(config):
        executor = mesos_pb2.ExecutorInfo()
        executor.name = config['name']
        executor.executor_id.value = config['id']
        executor.command.value = config['command']
        return executor

    def framework_info(config):
        framework = mesos_pb2.FrameworkInfo()
        framework.user = config.get('user', '')
        framework.name = config['name']
        return framework

    def task_info(data, scheduler, offer):
        task = mesos_pb2.TaskInfo()
        task.task_id.value = str(data.pop('id', scheduler.task_stats['created']).zfill(5))
        task.slave_id.value = offer.slave_id.value
        task.name = '%s %s' % (scheduler.name, task.task_id.value)
        task.executor.MergeFrom(scheduler.task_executor)
        task.data = data.get('msg', '') if isinstance(data, dict) else data
        return task

    def filters(config):
        filters = mesos_pb2.Filters()
        filters.refuse_seconds = config.get('filter_refuse_seconds', 300)
        return filters

    return locals().get(name)(*args, **kwargs)
