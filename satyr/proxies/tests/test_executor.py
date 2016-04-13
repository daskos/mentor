from mesos.interface import mesos_pb2
from satyr.proxies import ExecutorDriverProxy, ExecutorProxy
from satyr.proxies.messages import TaskStatus


def test_executor_event_handlers(mocker):
    executor = mocker.Mock()
    driver = mocker.Mock()
    proxy = ExecutorProxy(executor)

    proxy.registered(driver, mesos_pb2.ExecutorInfo(), mesos_pb2.FrameworkInfo(),
                     mesos_pb2.SlaveInfo())
    proxy.reregistered(driver, mesos_pb2.SlaveInfo())
    proxy.disconnected(driver)
    proxy.launchTask(driver, mesos_pb2.TaskInfo())
    proxy.killTask(driver, mesos_pb2.TaskID())
    proxy.frameworkMessage(driver, 'message')
    proxy.shutdown(driver)
    proxy.error(driver, 'message')

    executor.on_registered.assert_called_once()
    executor.on_reregistered.assert_called_once()
    executor.on_disconnected.assert_called_once()
    executor.on_launch.assert_called_once()
    executor.on_kill.assert_called_once()
    executor.on_message.assert_called_once()
    executor.on_shutdown.assert_called_once()
    executor.on_error.assert_called_once()


def test_executor_driver_callbacks(mocker):
    driver = mocker.Mock()
    proxy = ExecutorDriverProxy(driver)

    proxy.abort()
    proxy.join()
    proxy.start()
    proxy.stop()
    proxy.run()
    proxy.update(TaskStatus())
    proxy.message('message')

    driver.abort.assert_called_once()
    driver.join.assert_called_once()
    driver.start.assert_called_once()
    driver.stop.assert_called_once()
    driver.run.assert_called_once()
    driver.sendStatusUpdate.assert_called_once()
    driver.sendFrameworkMessage.assert_called_once()
