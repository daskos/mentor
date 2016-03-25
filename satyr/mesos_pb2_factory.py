from __future__ import absolute_import, division, print_function

from uuid import uuid4

from mesos.interface import mesos_pb2


def framework_info(config):
    framework = mesos_pb2.FrameworkInfo()
    framework.user = config['user']
    framework.name = config['name']
    return framework


def task_info(data, scheduler, executor, offer):
    task = mesos_pb2.TaskInfo()
    task.task_id.value = str(
        data.pop('id', scheduler.task_stats['created'])).zfill(5)
    task.slave_id.value = offer.slave_id.value
    task.name = '%s-%s' % (executor.name, task.task_id.value)
    task.executor.MergeFrom(executor)
    task.data = data.get('msg', '') if isinstance(data, dict) else data
    return task


def executor_info(config, data={}):
    executor = mesos_pb2.ExecutorInfo()
    executor.name = config['name']
    executor.executor_id.value = str(uuid4())

    command = build('command_info', config['command'])
    executor.command.MergeFrom(command)

    if data.get('image'):
        container = build('container_info')
        docker = build('docker_info', data['image'])
        container.docker.MergeFrom(docker)
        executor.container.MergeFrom(container)

    return executor


def command_info(command_string):
    command = mesos_pb2.CommandInfo()
    command.value = command_string
    command.shell = True
    return command


def container_info():
    container = mesos_pb2.ContainerInfo()
    container.type = 1  # docker
    return container


def docker_info(image):
    docker = mesos_pb2.ContainerInfo.DockerInfo()
    docker.image = image
    docker.network = 1  # HOST
    docker.force_pull_image = False
    return docker


def filters(config):
    filters = mesos_pb2.Filters()
    filters.refuse_seconds = config['filter_refuse_seconds']
    return filters
