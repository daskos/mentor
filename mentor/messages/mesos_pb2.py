from mentor.messages.protobuf_utils import *

class DiscoveryInfo(Message):
    class Visibility:
        FRAMEWORK = 0
        EXTERNAL = 2
        CLUSTER = 1

    visibility = None
    name = None
    environment = None
    location = None
    version = None
    ports = None
    labels = None

    def __init__(self):
        self.__lookup__ = [("required", type_enum, "visibility", 1),
                           ("optional", type_string, "name", 2),
                           ("optional", type_string, "environment", 3),
                           ("optional", type_string, "location", 4),
                           ("optional", type_string, "version", 5),
                           ("optional", Ports, "ports", 6),
                           ("optional", Labels, "labels", 7)]

class ResourceUsage(Message):
    class Executor(Message):
        class Task(Message):
            name = None
            id = None
            resources = None
            labels = None

            def __init__(self):
                self.__lookup__ = [("required", type_string, "name", 1),
                                   ("required", TaskID, "id", 2),
                                   ("repeated", Resource, "resources", 3),
                                   ("optional", Labels, "labels", 4)]

        executor_info = None
        allocated = None
        statistics = None
        container_id = None
        tasks = None

        def __init__(self):
            self.__lookup__ = [("required", ExecutorInfo, "executor_info", 1),
                               ("repeated", Resource, "allocated", 2),
                               ("optional", ResourceStatistics, "statistics", 3),
                               ("required", ContainerID, "container_id", 4),
                               ("repeated", ResourceUsage.Executor.Task, "tasks", 5)]

    executors = None
    total = None

    def __init__(self):
        self.__lookup__ = [("repeated", ResourceUsage.Executor, "executors", 1),
                           ("repeated", Resource, "total", 2)]

class Parameters(Message):
    parameter = None

    def __init__(self):
        self.__lookup__ = [("repeated", Parameter, "parameter", 1)]

class CheckStatusInfo(Message):
    class Http(Message):
        status_code = None

        def __init__(self):
            self.__lookup__ = [("optional", type_uint32, "status_code", 1)]

    class Command(Message):
        exit_code = None

        def __init__(self):
            self.__lookup__ = [("optional", type_int32, "exit_code", 1)]

    type = None
    command = None
    http = None

    def __init__(self):
        self.__lookup__ = [("optional", type_enum, "type", 1),
                           ("optional", CheckStatusInfo.Command, "command", 2),
                           ("optional", CheckStatusInfo.Http, "http", 3)]

class TaskState:
    TASK_ERROR = 7
    TASK_KILLED = 4
    TASK_STAGING = 6
    TASK_FAILED = 3
    TASK_FINISHED = 2
    TASK_UNKNOWN = 13
    TASK_GONE_BY_OPERATOR = 12
    TASK_RUNNING = 1
    TASK_LOST = 5
    TASK_KILLING = 8
    TASK_UNREACHABLE = 10
    TASK_STARTING = 0
    TASK_DROPPED = 9
    TASK_GONE = 11

class MachineInfo(Message):
    class Mode:
        DOWN = 3
        DRAINING = 2
        UP = 1

    id = None
    mode = None
    unavailability = None

    def __init__(self):
        self.__lookup__ = [("required", MachineID, "id", 1),
                           ("optional", type_enum, "mode", 2),
                           ("optional", Unavailability, "unavailability", 3)]

class TaskGroupInfo(Message):
    tasks = None

    def __init__(self):
        self.__lookup__ = [("repeated", TaskInfo, "tasks", 1)]

class OfferID(Message):
    value = None

    def __init__(self):
        self.__lookup__ = [("required", type_string, "value", 1)]

class Label(Message):
    key = None
    value = None

    def __init__(self):
        self.__lookup__ = [("required", type_string, "key", 1),
                           ("optional", type_string, "value", 2)]

class Environment(Message):
    class Variable(Message):
        name = None
        value = None

        def __init__(self):
            self.__lookup__ = [("required", type_string, "name", 1),
                               ("required", type_string, "value", 2)]

    variables = None

    def __init__(self):
        self.__lookup__ = [("repeated", Environment.Variable, "variables", 1)]

class RateLimit(Message):
    qps = None
    principal = None
    capacity = None

    def __init__(self):
        self.__lookup__ = [("optional", type_double, "qps", 1),
                           ("required", type_string, "principal", 2),
                           ("optional", type_uint64, "capacity", 3)]

class Role(Message):
    name = None
    weight = None
    frameworks = None
    resources = None

    def __init__(self):
        self.__lookup__ = [("required", type_string, "name", 1),
                           ("required", type_double, "weight", 2),
                           ("repeated", FrameworkID, "frameworks", 3),
                           ("repeated", Resource, "resources", 4)]

class Resource(Message):
    class RevocableInfo(Message):
        pass

    class SharedInfo(Message):
        pass

    class AllocationInfo(Message):
        role = None

        def __init__(self):
            self.__lookup__ = [("optional", type_string, "role", 1)]

    class ReservationInfo(Message):
        principal = None
        labels = None

        def __init__(self):
            self.__lookup__ = [("optional", type_string, "principal", 1),
                               ("optional", Labels, "labels", 2)]

    class DiskInfo(Message):
        class Source(Message):
            class Path(Message):
                root = None

                def __init__(self):
                    self.__lookup__ = [("required", type_string, "root", 1)]

            class Mount(Message):
                root = None

                def __init__(self):
                    self.__lookup__ = [("required", type_string, "root", 1)]

            class Type:
                PATH = 1
                MOUNT = 2

            type = None
            path = None
            mount = None

            def __init__(self):
                self.__lookup__ = [("required", type_enum, "type", 1),
                                   ("optional", Resource.DiskInfo.Source.Path, "path", 2),
                                   ("optional", Resource.DiskInfo.Source.Mount, "mount", 3)]

        class Persistence(Message):
            id = None
            principal = None

            def __init__(self):
                self.__lookup__ = [("required", type_string, "id", 1),
                                   ("optional", type_string, "principal", 2)]

        persistence = None
        volume = None
        source = None

        def __init__(self):
            self.__lookup__ = [("optional", Resource.DiskInfo.Persistence, "persistence", 1),
                               ("optional", Volume, "volume", 2),
                               ("optional", Resource.DiskInfo.Source, "source", 3)]

    name = None
    type = None
    scalar = None
    ranges = None
    set = None
    allocation_info = None
    reservation = None
    disk = None
    revocable = None
    shared = None

    def __init__(self):
        self.__lookup__ = [("required", type_string, "name", 1),
                           ("required", type_enum, "type", 2),
                           ("optional", Value.Scalar, "scalar", 3),
                           ("optional", Value.Ranges, "ranges", 4),
                           ("optional", Value.Set, "set", 5),
                           ("optional", Resource.AllocationInfo, "allocation_info", 11),
                           ("optional", Resource.ReservationInfo, "reservation", 8),
                           ("optional", Resource.DiskInfo, "disk", 7),
                           ("optional", Resource.RevocableInfo, "revocable", 9),
                           ("optional", Resource.SharedInfo, "shared", 10)]

class Port(Message):
    number = None
    name = None
    protocol = None
    visibility = None
    labels = None

    def __init__(self):
        self.__lookup__ = [("required", type_uint32, "number", 1),
                           ("optional", type_string, "name", 2),
                           ("optional", type_string, "protocol", 3),
                           ("optional", type_enum, "visibility", 4),
                           ("optional", Labels, "labels", 5)]

class Parameter(Message):
    key = None
    value = None

    def __init__(self):
        self.__lookup__ = [("required", type_string, "key", 1),
                           ("required", type_string, "value", 2)]

class ResourceStatistics(Message):
    timestamp = None
    processes = None
    threads = None
    cpus_user_time_secs = None
    cpus_system_time_secs = None
    cpus_limit = None
    cpus_nr_periods = None
    cpus_nr_throttled = None
    cpus_throttled_time_secs = None
    mem_total_bytes = None
    mem_total_memsw_bytes = None
    mem_limit_bytes = None
    mem_soft_limit_bytes = None
    mem_file_bytes = None
    mem_anon_bytes = None
    mem_cache_bytes = None
    mem_rss_bytes = None
    mem_mapped_file_bytes = None
    mem_swap_bytes = None
    mem_unevictable_bytes = None
    mem_low_pressure_counter = None
    mem_medium_pressure_counter = None
    mem_critical_pressure_counter = None
    disk_limit_bytes = None
    disk_used_bytes = None
    perf = None
    net_rx_packets = None
    net_rx_bytes = None
    net_rx_errors = None
    net_rx_dropped = None
    net_tx_packets = None
    net_tx_bytes = None
    net_tx_errors = None
    net_tx_dropped = None
    net_tcp_rtt_microsecs_p50 = None
    net_tcp_rtt_microsecs_p90 = None
    net_tcp_rtt_microsecs_p95 = None
    net_tcp_rtt_microsecs_p99 = None
    net_tcp_active_connections = None
    net_tcp_time_wait_connections = None
    net_traffic_control_statistics = None
    net_snmp_statistics = None

    def __init__(self):
        self.__lookup__ = [("required", type_double, "timestamp", 1),
                           ("optional", type_uint32, "processes", 30),
                           ("optional", type_uint32, "threads", 31),
                           ("optional", type_double, "cpus_user_time_secs", 2),
                           ("optional", type_double, "cpus_system_time_secs", 3),
                           ("optional", type_double, "cpus_limit", 4),
                           ("optional", type_uint32, "cpus_nr_periods", 7),
                           ("optional", type_uint32, "cpus_nr_throttled", 8),
                           ("optional", type_double, "cpus_throttled_time_secs", 9),
                           ("optional", type_uint64, "mem_total_bytes", 36),
                           ("optional", type_uint64, "mem_total_memsw_bytes", 37),
                           ("optional", type_uint64, "mem_limit_bytes", 6),
                           ("optional", type_uint64, "mem_soft_limit_bytes", 38),
                           ("optional", type_uint64, "mem_file_bytes", 10),
                           ("optional", type_uint64, "mem_anon_bytes", 11),
                           ("optional", type_uint64, "mem_cache_bytes", 39),
                           ("optional", type_uint64, "mem_rss_bytes", 5),
                           ("optional", type_uint64, "mem_mapped_file_bytes", 12),
                           ("optional", type_uint64, "mem_swap_bytes", 40),
                           ("optional", type_uint64, "mem_unevictable_bytes", 41),
                           ("optional", type_uint64, "mem_low_pressure_counter", 32),
                           ("optional", type_uint64, "mem_medium_pressure_counter", 33),
                           ("optional", type_uint64, "mem_critical_pressure_counter", 34),
                           ("optional", type_uint64, "disk_limit_bytes", 26),
                           ("optional", type_uint64, "disk_used_bytes", 27),
                           ("optional", PerfStatistics, "perf", 13),
                           ("optional", type_uint64, "net_rx_packets", 14),
                           ("optional", type_uint64, "net_rx_bytes", 15),
                           ("optional", type_uint64, "net_rx_errors", 16),
                           ("optional", type_uint64, "net_rx_dropped", 17),
                           ("optional", type_uint64, "net_tx_packets", 18),
                           ("optional", type_uint64, "net_tx_bytes", 19),
                           ("optional", type_uint64, "net_tx_errors", 20),
                           ("optional", type_uint64, "net_tx_dropped", 21),
                           ("optional", type_double, "net_tcp_rtt_microsecs_p50", 22),
                           ("optional", type_double, "net_tcp_rtt_microsecs_p90", 23),
                           ("optional", type_double, "net_tcp_rtt_microsecs_p95", 24),
                           ("optional", type_double, "net_tcp_rtt_microsecs_p99", 25),
                           ("optional", type_double, "net_tcp_active_connections", 28),
                           ("optional", type_double, "net_tcp_time_wait_connections", 29),
                           ("repeated", TrafficControlStatistics, "net_traffic_control_statistics", 35),
                           ("optional", SNMPStatistics, "net_snmp_statistics", 42)]

class Status:
    DRIVER_RUNNING = 2
    DRIVER_ABORTED = 3
    DRIVER_NOT_STARTED = 1
    DRIVER_STOPPED = 4

class FrameworkInfo(Message):
    class Capability(Message):
        class Type:
            MULTI_ROLE = 6
            UNKNOWN = 0
            SHARED_RESOURCES = 4
            REVOCABLE_RESOURCES = 1
            GPU_RESOURCES = 3
            TASK_KILLING_STATE = 2
            PARTITION_AWARE = 5

        type = None

        def __init__(self):
            self.__lookup__ = [("optional", type_enum, "type", 1)]

    user = None
    name = None
    id = None
    failover_timeout = None
    checkpoint = None
    roles = None
    hostname = None
    principal = None
    webui_url = None
    capabilities = None
    labels = None

    def __init__(self):
        self.__lookup__ = [("required", type_string, "user", 1),
                           ("required", type_string, "name", 2),
                           ("optional", FrameworkID, "id", 3),
                           ("optional", type_double, "failover_timeout", 4),
                           ("optional", type_bool, "checkpoint", 5),
                           ("repeated", type_string, "roles", 12),
                           ("optional", type_string, "hostname", 7),
                           ("optional", type_string, "principal", 8),
                           ("optional", type_string, "webui_url", 9),
                           ("repeated", FrameworkInfo.Capability, "capabilities", 10),
                           ("optional", Labels, "labels", 11)]

        self.failover_timeout = 0.0
        self.checkpoint = False

class SlaveInfo(Message):
    class Capability(Message):
        class Type:
            MULTI_ROLE = 1
            UNKNOWN = 0

        type = None

        def __init__(self):
            self.__lookup__ = [("optional", type_enum, "type", 1)]

    hostname = None
    port = None
    resources = None
    attributes = None
    id = None
    checkpoint = None

    def __init__(self):
        self.__lookup__ = [("required", type_string, "hostname", 1),
                           ("optional", type_int32, "port", 8),
                           ("repeated", Resource, "resources", 3),
                           ("repeated", Attribute, "attributes", 5),
                           ("optional", SlaveID, "id", 6),
                           ("optional", type_bool, "checkpoint", 7)]

        self.port = 5051
        self.checkpoint = False

class Offer(Message):
    class Operation(Message):
        class LaunchGroup(Message):
            executor = None
            task_group = None

            def __init__(self):
                self.__lookup__ = [("required", ExecutorInfo, "executor", 1),
                                   ("required", TaskGroupInfo, "task_group", 2)]

        class Launch(Message):
            task_infos = None

            def __init__(self):
                self.__lookup__ = [("repeated", TaskInfo, "task_infos", 1)]

        class Create(Message):
            volumes = None

            def __init__(self):
                self.__lookup__ = [("repeated", Resource, "volumes", 1)]

        class Unreserve(Message):
            resources = None

            def __init__(self):
                self.__lookup__ = [("repeated", Resource, "resources", 1)]

        class Destroy(Message):
            volumes = None

            def __init__(self):
                self.__lookup__ = [("repeated", Resource, "volumes", 1)]

        class Type:
            LAUNCH_GROUP = 6
            LAUNCH = 1
            UNKNOWN = 0
            CREATE = 4
            UNRESERVE = 3
            DESTROY = 5
            RESERVE = 2

        class Reserve(Message):
            resources = None

            def __init__(self):
                self.__lookup__ = [("repeated", Resource, "resources", 1)]

        type = None
        launch = None
        launch_group = None
        reserve = None
        unreserve = None
        create = None
        destroy = None

        def __init__(self):
            self.__lookup__ = [("optional", type_enum, "type", 1),
                               ("optional", Offer.Operation.Launch, "launch", 2),
                               ("optional", Offer.Operation.LaunchGroup, "launch_group", 7),
                               ("optional", Offer.Operation.Reserve, "reserve", 3),
                               ("optional", Offer.Operation.Unreserve, "unreserve", 4),
                               ("optional", Offer.Operation.Create, "create", 5),
                               ("optional", Offer.Operation.Destroy, "destroy", 6)]

    id = None
    framework_id = None
    slave_id = None
    hostname = None
    url = None
    resources = None
    attributes = None
    executor_ids = None
    unavailability = None
    allocation_info = None

    def __init__(self):
        self.__lookup__ = [("required", OfferID, "id", 1),
                           ("required", FrameworkID, "framework_id", 2),
                           ("required", SlaveID, "slave_id", 3),
                           ("required", type_string, "hostname", 4),
                           ("optional", URL, "url", 8),
                           ("repeated", Resource, "resources", 5),
                           ("repeated", Attribute, "attributes", 7),
                           ("repeated", ExecutorID, "executor_ids", 6),
                           ("optional", Unavailability, "unavailability", 9),
                           ("optional", Resource.AllocationInfo, "allocation_info", 10)]

class MachineID(Message):
    hostname = None
    ip = None

    def __init__(self):
        self.__lookup__ = [("optional", type_string, "hostname", 1),
                           ("optional", type_string, "ip", 2)]

class TTYInfo(Message):
    class WindowSize(Message):
        rows = None
        columns = None

        def __init__(self):
            self.__lookup__ = [("required", type_uint32, "rows", 1),
                               ("required", type_uint32, "columns", 2)]

    window_size = None

    def __init__(self):
        self.__lookup__ = [("optional", TTYInfo.WindowSize, "window_size", 1)]

class FrameworkID(Message):
    value = None

    def __init__(self):
        self.__lookup__ = [("required", type_string, "value", 1)]

class ExecutorID(Message):
    value = None

    def __init__(self):
        self.__lookup__ = [("required", type_string, "value", 1)]

class Volume(Message):
    class Source(Message):
        class SandboxPath(Message):
            class Type:
                UNKNOWN = 0
                SELF = 1
                PARENT = 2

            type = None
            path = None

            def __init__(self):
                self.__lookup__ = [("optional", type_enum, "type", 1),
                                   ("required", type_string, "path", 2)]

        class Type:
            UNKNOWN = 0
            DOCKER_VOLUME = 1
            SANDBOX_PATH = 2

        class DockerVolume(Message):
            driver = None
            name = None
            driver_options = None

            def __init__(self):
                self.__lookup__ = [("optional", type_string, "driver", 1),
                                   ("required", type_string, "name", 2),
                                   ("optional", Parameters, "driver_options", 3)]

        type = None
        docker_volume = None
        sandbox_path = None

        def __init__(self):
            self.__lookup__ = [("optional", type_enum, "type", 1),
                               ("optional", Volume.Source.DockerVolume, "docker_volume", 2),
                               ("optional", Volume.Source.SandboxPath, "sandbox_path", 3)]

    class Mode:
        RO = 2
        RW = 1

    mode = None
    container_path = None
    host_path = None
    image = None
    source = None

    def __init__(self):
        self.__lookup__ = [("required", type_enum, "mode", 3),
                           ("required", type_string, "container_path", 1),
                           ("optional", type_string, "host_path", 2),
                           ("optional", Image, "image", 4),
                           ("optional", Volume.Source, "source", 5)]

class IcmpStatistics(Message):
    InMsgs = None
    InErrors = None
    InCsumErrors = None
    InDestUnreachs = None
    InTimeExcds = None
    InParmProbs = None
    InSrcQuenchs = None
    InRedirects = None
    InEchos = None
    InEchoReps = None
    InTimestamps = None
    InTimestampReps = None
    InAddrMasks = None
    InAddrMaskReps = None
    OutMsgs = None
    OutErrors = None
    OutDestUnreachs = None
    OutTimeExcds = None
    OutParmProbs = None
    OutSrcQuenchs = None
    OutRedirects = None
    OutEchos = None
    OutEchoReps = None
    OutTimestamps = None
    OutTimestampReps = None
    OutAddrMasks = None
    OutAddrMaskReps = None

    def __init__(self):
        self.__lookup__ = [("optional", type_int64, "InMsgs", 1),
                           ("optional", type_int64, "InErrors", 2),
                           ("optional", type_int64, "InCsumErrors", 3),
                           ("optional", type_int64, "InDestUnreachs", 4),
                           ("optional", type_int64, "InTimeExcds", 5),
                           ("optional", type_int64, "InParmProbs", 6),
                           ("optional", type_int64, "InSrcQuenchs", 7),
                           ("optional", type_int64, "InRedirects", 8),
                           ("optional", type_int64, "InEchos", 9),
                           ("optional", type_int64, "InEchoReps", 10),
                           ("optional", type_int64, "InTimestamps", 11),
                           ("optional", type_int64, "InTimestampReps", 12),
                           ("optional", type_int64, "InAddrMasks", 13),
                           ("optional", type_int64, "InAddrMaskReps", 14),
                           ("optional", type_int64, "OutMsgs", 15),
                           ("optional", type_int64, "OutErrors", 16),
                           ("optional", type_int64, "OutDestUnreachs", 17),
                           ("optional", type_int64, "OutTimeExcds", 18),
                           ("optional", type_int64, "OutParmProbs", 19),
                           ("optional", type_int64, "OutSrcQuenchs", 20),
                           ("optional", type_int64, "OutRedirects", 21),
                           ("optional", type_int64, "OutEchos", 22),
                           ("optional", type_int64, "OutEchoReps", 23),
                           ("optional", type_int64, "OutTimestamps", 24),
                           ("optional", type_int64, "OutTimestampReps", 25),
                           ("optional", type_int64, "OutAddrMasks", 26),
                           ("optional", type_int64, "OutAddrMaskReps", 27)]

class Flag(Message):
    name = None
    value = None

    def __init__(self):
        self.__lookup__ = [("required", type_string, "name", 1),
                           ("optional", type_string, "value", 2)]

class Metric(Message):
    name = None
    value = None

    def __init__(self):
        self.__lookup__ = [("required", type_string, "name", 1),
                           ("optional", type_double, "value", 2)]

class Address(Message):
    hostname = None
    ip = None
    port = None

    def __init__(self):
        self.__lookup__ = [("optional", type_string, "hostname", 1),
                           ("optional", type_string, "ip", 2),
                           ("required", type_int32, "port", 3)]

class MasterInfo(Message):
    id = None
    ip = None
    port = None
    pid = None
    hostname = None
    version = None
    address = None

    def __init__(self):
        self.__lookup__ = [("required", type_string, "id", 1),
                           ("required", type_uint32, "ip", 2),
                           ("required", type_uint32, "port", 3),
                           ("optional", type_string, "pid", 4),
                           ("optional", type_string, "hostname", 5),
                           ("optional", type_string, "version", 6),
                           ("optional", Address, "address", 7)]

        self.port = 5050

class Credentials(Message):
    credentials = None

    def __init__(self):
        self.__lookup__ = [("repeated", Credential, "credentials", 1)]

class ContainerInfo(Message):
    class DockerInfo(Message):
        class Network:
            BRIDGE = 2
            HOST = 1
            NONE = 3
            USER = 4

        class PortMapping(Message):
            host_port = None
            container_port = None
            protocol = None

            def __init__(self):
                self.__lookup__ = [("required", type_uint32, "host_port", 1),
                                   ("required", type_uint32, "container_port", 2),
                                   ("optional", type_string, "protocol", 3)]

        image = None
        network = None
        port_mappings = None
        privileged = None
        parameters = None
        force_pull_image = None
        volume_driver = None

        def __init__(self):
            self.__lookup__ = [("required", type_string, "image", 1),
                               ("optional", type_enum, "network", 2),
                               ("repeated", ContainerInfo.DockerInfo.PortMapping, "port_mappings", 3),
                               ("optional", type_bool, "privileged", 4),
                               ("repeated", Parameter, "parameters", 5),
                               ("optional", type_bool, "force_pull_image", 6),
                               ("optional", type_string, "volume_driver", 7)]

            self.network = 1
            self.privileged = False

    class Type:
        DOCKER = 1
        MESOS = 2

    class MesosInfo(Message):
        image = None

        def __init__(self):
            self.__lookup__ = [("optional", Image, "image", 1)]

    type = None
    volumes = None
    hostname = None
    docker = None
    mesos = None
    network_infos = None
    linux_info = None
    rlimit_info = None
    tty_info = None

    def __init__(self):
        self.__lookup__ = [("required", type_enum, "type", 1),
                           ("repeated", Volume, "volumes", 2),
                           ("optional", type_string, "hostname", 4),
                           ("optional", ContainerInfo.DockerInfo, "docker", 3),
                           ("optional", ContainerInfo.MesosInfo, "mesos", 5),
                           ("repeated", NetworkInfo, "network_infos", 7),
                           ("optional", LinuxInfo, "linux_info", 8),
                           ("optional", RLimitInfo, "rlimit_info", 9),
                           ("optional", TTYInfo, "tty_info", 10)]

class Filters(Message):
    refuse_seconds = None

    def __init__(self):
        self.__lookup__ = [("optional", type_double, "refuse_seconds", 1)]

        self.refuse_seconds = 5.0

class Task(Message):
    name = None
    task_id = None
    framework_id = None
    executor_id = None
    slave_id = None
    state = None
    resources = None
    statuses = None
    status_update_state = None
    status_update_uuid = None
    labels = None
    discovery = None
    container = None
    user = None

    def __init__(self):
        self.__lookup__ = [("required", type_string, "name", 1),
                           ("required", TaskID, "task_id", 2),
                           ("required", FrameworkID, "framework_id", 3),
                           ("optional", ExecutorID, "executor_id", 4),
                           ("required", SlaveID, "slave_id", 5),
                           ("required", type_enum, "state", 6),
                           ("repeated", Resource, "resources", 7),
                           ("repeated", TaskStatus, "statuses", 8),
                           ("optional", type_enum, "status_update_state", 9),
                           ("optional", type_bytes, "status_update_uuid", 10),
                           ("optional", Labels, "labels", 11),
                           ("optional", DiscoveryInfo, "discovery", 12),
                           ("optional", ContainerInfo, "container", 13),
                           ("optional", type_string, "user", 14)]

class KillPolicy(Message):
    grace_period = None

    def __init__(self):
        self.__lookup__ = [("optional", DurationInfo, "grace_period", 1)]

class ContainerID(Message):
    value = None
    parent = None

    def __init__(self):
        self.__lookup__ = [("required", type_string, "value", 1),
                           ("optional", ContainerID, "parent", 2)]

class IpStatistics(Message):
    Forwarding = None
    DefaultTTL = None
    InReceives = None
    InHdrErrors = None
    InAddrErrors = None
    ForwDatagrams = None
    InUnknownProtos = None
    InDiscards = None
    InDelivers = None
    OutRequests = None
    OutDiscards = None
    OutNoRoutes = None
    ReasmTimeout = None
    ReasmReqds = None
    ReasmOKs = None
    ReasmFails = None
    FragOKs = None
    FragFails = None
    FragCreates = None

    def __init__(self):
        self.__lookup__ = [("optional", type_int64, "Forwarding", 1),
                           ("optional", type_int64, "DefaultTTL", 2),
                           ("optional", type_int64, "InReceives", 3),
                           ("optional", type_int64, "InHdrErrors", 4),
                           ("optional", type_int64, "InAddrErrors", 5),
                           ("optional", type_int64, "ForwDatagrams", 6),
                           ("optional", type_int64, "InUnknownProtos", 7),
                           ("optional", type_int64, "InDiscards", 8),
                           ("optional", type_int64, "InDelivers", 9),
                           ("optional", type_int64, "OutRequests", 10),
                           ("optional", type_int64, "OutDiscards", 11),
                           ("optional", type_int64, "OutNoRoutes", 12),
                           ("optional", type_int64, "ReasmTimeout", 13),
                           ("optional", type_int64, "ReasmReqds", 14),
                           ("optional", type_int64, "ReasmOKs", 15),
                           ("optional", type_int64, "ReasmFails", 16),
                           ("optional", type_int64, "FragOKs", 17),
                           ("optional", type_int64, "FragFails", 18),
                           ("optional", type_int64, "FragCreates", 19)]

class Credential(Message):
    principal = None
    secret = None

    def __init__(self):
        self.__lookup__ = [("required", type_string, "principal", 1),
                           ("optional", type_string, "secret", 2)]

class URL(Message):
    scheme = None
    address = None
    path = None
    query = None
    fragment = None

    def __init__(self):
        self.__lookup__ = [("required", type_string, "scheme", 1),
                           ("required", Address, "address", 2),
                           ("optional", type_string, "path", 3),
                           ("repeated", Parameter, "query", 4),
                           ("optional", type_string, "fragment", 5)]

class HealthCheck(Message):
    class HTTPCheckInfo(Message):
        scheme = None
        port = None
        path = None
        statuses = None

        def __init__(self):
            self.__lookup__ = [("optional", type_string, "scheme", 3),
                               ("required", type_uint32, "port", 1),
                               ("optional", type_string, "path", 2),
                               ("repeated", type_uint32, "statuses", 4)]

    class Type:
        UNKNOWN = 0
        HTTP = 2
        COMMAND = 1
        TCP = 3

    class TCPCheckInfo(Message):
        port = None

        def __init__(self):
            self.__lookup__ = [("required", type_uint32, "port", 1)]

    delay_seconds = None
    interval_seconds = None
    timeout_seconds = None
    consecutive_failures = None
    grace_period_seconds = None
    type = None
    command = None
    http = None
    tcp = None

    def __init__(self):
        self.__lookup__ = [("optional", type_double, "delay_seconds", 2),
                           ("optional", type_double, "interval_seconds", 3),
                           ("optional", type_double, "timeout_seconds", 4),
                           ("optional", type_uint32, "consecutive_failures", 5),
                           ("optional", type_double, "grace_period_seconds", 6),
                           ("optional", type_enum, "type", 8),
                           ("optional", CommandInfo, "command", 7),
                           ("optional", HealthCheck.HTTPCheckInfo, "http", 1),
                           ("optional", HealthCheck.TCPCheckInfo, "tcp", 9)]

        self.delay_seconds = 15.0
        self.interval_seconds = 10.0
        self.timeout_seconds = 20.0
        self.consecutive_failures = 3
        self.grace_period_seconds = 10.0

class Request(Message):
    slave_id = None
    resources = None

    def __init__(self):
        self.__lookup__ = [("optional", SlaveID, "slave_id", 1),
                           ("repeated", Resource, "resources", 2)]

class Value(Message):
    class Set(Message):
        item = None

        def __init__(self):
            self.__lookup__ = [("repeated", type_string, "item", 1)]

    class Text(Message):
        value = None

        def __init__(self):
            self.__lookup__ = [("required", type_string, "value", 1)]

    class Range(Message):
        begin = None
        end = None

        def __init__(self):
            self.__lookup__ = [("required", type_uint64, "begin", 1),
                               ("required", type_uint64, "end", 2)]

    class Ranges(Message):
        range = None

        def __init__(self):
            self.__lookup__ = [("repeated", Value.Range, "range", 1)]

    class Scalar(Message):
        value = None

        def __init__(self):
            self.__lookup__ = [("required", type_double, "value", 1)]

    class Type:
        RANGES = 1
        TEXT = 3
        SCALAR = 0
        SET = 2

    type = None
    scalar = None
    ranges = None
    set = None
    text = None

    def __init__(self):
        self.__lookup__ = [("required", type_enum, "type", 1),
                           ("optional", Value.Scalar, "scalar", 2),
                           ("optional", Value.Ranges, "ranges", 3),
                           ("optional", Value.Set, "set", 4),
                           ("optional", Value.Text, "text", 5)]

class TaskStatus(Message):
    class Source:
        SOURCE_MASTER = 0
        SOURCE_EXECUTOR = 2
        SOURCE_SLAVE = 1

    class Reason:
        REASON_SLAVE_REMOVED = 11
        REASON_INVALID_FRAMEWORKID = 5
        REASON_CONTAINER_LAUNCH_FAILED = 21
        REASON_EXECUTOR_UNREGISTERED = 2
        REASON_TASK_GROUP_UNAUTHORIZED = 26
        REASON_CONTAINER_LIMITATION = 19
        REASON_GC_ERROR = 4
        REASON_TASK_INVALID = 14
        REASON_SLAVE_DISCONNECTED = 10
        REASON_RESOURCES_UNKNOWN = 18
        REASON_CONTAINER_LIMITATION_DISK = 20
        REASON_SLAVE_UNKNOWN = 13
        REASON_TASK_UNKNOWN = 16
        REASON_CONTAINER_LIMITATION_MEMORY = 8
        REASON_CONTAINER_UPDATE_FAILED = 22
        REASON_MASTER_DISCONNECTED = 7
        REASON_EXECUTOR_REREGISTRATION_TIMEOUT = 24
        REASON_EXECUTOR_TERMINATED = 1
        REASON_EXECUTOR_REGISTRATION_TIMEOUT = 23
        REASON_TASK_GROUP_INVALID = 25
        REASON_FRAMEWORK_REMOVED = 3
        REASON_SLAVE_RESTARTED = 12
        REASON_TASK_UNAUTHORIZED = 15
        REASON_COMMAND_EXECUTOR_FAILED = 0
        REASON_RECONCILIATION = 9
        REASON_IO_SWITCHBOARD_EXITED = 27
        REASON_CONTAINER_PREEMPTED = 17
        REASON_TASK_CHECK_STATUS_UPDATED = 28
        REASON_INVALID_OFFERS = 6

    task_id = None
    state = None
    message = None
    source = None
    reason = None
    data = None
    slave_id = None
    executor_id = None
    timestamp = None
    uuid = None
    healthy = None
    check_status = None
    labels = None
    container_status = None
    unreachable_time = None

    def __init__(self):
        self.__lookup__ = [("required", TaskID, "task_id", 1),
                           ("required", type_enum, "state", 2),
                           ("optional", type_string, "message", 4),
                           ("optional", type_enum, "source", 9),
                           ("optional", type_enum, "reason", 10),
                           ("optional", type_bytes, "data", 3),
                           ("optional", SlaveID, "slave_id", 5),
                           ("optional", ExecutorID, "executor_id", 7),
                           ("optional", type_double, "timestamp", 6),
                           ("optional", type_bytes, "uuid", 11),
                           ("optional", type_bool, "healthy", 8),
                           ("optional", CheckStatusInfo, "check_status", 15),
                           ("optional", Labels, "labels", 12),
                           ("optional", ContainerStatus, "container_status", 13),
                           ("optional", TimeInfo, "unreachable_time", 14)]

class DurationInfo(Message):
    nanoseconds = None

    def __init__(self):
        self.__lookup__ = [("required", type_int64, "nanoseconds", 1)]

class InverseOffer(Message):
    id = None
    url = None
    framework_id = None
    slave_id = None
    unavailability = None
    resources = None

    def __init__(self):
        self.__lookup__ = [("required", OfferID, "id", 1),
                           ("optional", URL, "url", 2),
                           ("required", FrameworkID, "framework_id", 3),
                           ("optional", SlaveID, "slave_id", 4),
                           ("required", Unavailability, "unavailability", 5),
                           ("repeated", Resource, "resources", 6)]

class ExecutorInfo(Message):
    class Type:
        DEFAULT = 1
        UNKNOWN = 0
        CUSTOM = 2

    type = None
    executor_id = None
    framework_id = None
    command = None
    container = None
    resources = None
    name = None
    source = None
    data = None
    discovery = None
    shutdown_grace_period = None
    labels = None

    def __init__(self):
        self.__lookup__ = [("optional", type_enum, "type", 15),
                           ("required", ExecutorID, "executor_id", 1),
                           ("optional", FrameworkID, "framework_id", 8),
                           ("optional", CommandInfo, "command", 7),
                           ("optional", ContainerInfo, "container", 11),
                           ("repeated", Resource, "resources", 5),
                           ("optional", type_string, "name", 9),
                           ("optional", type_string, "source", 10),
                           ("optional", type_bytes, "data", 4),
                           ("optional", DiscoveryInfo, "discovery", 12),
                           ("optional", DurationInfo, "shutdown_grace_period", 13),
                           ("optional", Labels, "labels", 14)]

class UdpStatistics(Message):
    InDatagrams = None
    NoPorts = None
    InErrors = None
    OutDatagrams = None
    RcvbufErrors = None
    SndbufErrors = None
    InCsumErrors = None
    IgnoredMulti = None

    def __init__(self):
        self.__lookup__ = [("optional", type_int64, "InDatagrams", 1),
                           ("optional", type_int64, "NoPorts", 2),
                           ("optional", type_int64, "InErrors", 3),
                           ("optional", type_int64, "OutDatagrams", 4),
                           ("optional", type_int64, "RcvbufErrors", 5),
                           ("optional", type_int64, "SndbufErrors", 6),
                           ("optional", type_int64, "InCsumErrors", 7),
                           ("optional", type_int64, "IgnoredMulti", 8)]

class TaskID(Message):
    value = None

    def __init__(self):
        self.__lookup__ = [("required", type_string, "value", 1)]

class CapabilityInfo(Message):
    class Capability:
        SETUID = 1007
        MAC_ADMIN = 1033
        SYS_RESOURCE = 1024
        MAC_OVERRIDE = 1032
        UNKNOWN = 0
        SYS_BOOT = 1022
        NET_BIND_SERVICE = 1010
        BLOCK_SUSPEND = 1036
        NET_BROADCAST = 1011
        NET_ADMIN = 1012
        CHOWN = 1000
        KILL = 1005
        SYS_TIME = 1025
        SYS_RAWIO = 1017
        SYS_TTY_CONFIG = 1026
        SYS_NICE = 1023
        SYS_ADMIN = 1021
        IPC_OWNER = 1015
        SETGID = 1006
        SETPCAP = 1008
        SYS_MODULE = 1016
        SYS_PTRACE = 1019
        IPC_LOCK = 1014
        DAC_READ_SEARCH = 1002
        FSETID = 1004
        LINUX_IMMUTABLE = 1009
        FOWNER = 1003
        AUDIT_CONTROL = 1030
        SYS_PACCT = 1020
        LEASE = 1028
        SETFCAP = 1031
        SYSLOG = 1034
        SYS_CHROOT = 1018
        WAKE_ALARM = 1035
        AUDIT_WRITE = 1029
        DAC_OVERRIDE = 1001
        NET_RAW = 1013
        MKNOD = 1027
        AUDIT_READ = 1037

    capabilities = None

    def __init__(self):
        self.__lookup__ = [("repeated", type_enum, "capabilities", 1)]

class FileInfo(Message):
    path = None
    nlink = None
    size = None
    mtime = None
    mode = None
    uid = None
    gid = None

    def __init__(self):
        self.__lookup__ = [("required", type_string, "path", 1),
                           ("optional", type_int32, "nlink", 2),
                           ("optional", type_uint64, "size", 3),
                           ("optional", TimeInfo, "mtime", 4),
                           ("optional", type_uint32, "mode", 5),
                           ("optional", type_string, "uid", 6),
                           ("optional", type_string, "gid", 7)]

class LinuxInfo(Message):
    capability_info = None

    def __init__(self):
        self.__lookup__ = [("optional", CapabilityInfo, "capability_info", 1)]

class Ports(Message):
    ports = None

    def __init__(self):
        self.__lookup__ = [("repeated", Port, "ports", 1)]

class CgroupInfo(Message):
    class NetCls(Message):
        classid = None

        def __init__(self):
            self.__lookup__ = [("optional", type_uint32, "classid", 1)]

    net_cls = None

    def __init__(self):
        self.__lookup__ = [("optional", CgroupInfo.NetCls, "net_cls", 1)]

class VersionInfo(Message):
    version = None
    build_date = None
    build_time = None
    build_user = None
    git_sha = None
    git_branch = None
    git_tag = None

    def __init__(self):
        self.__lookup__ = [("required", type_string, "version", 1),
                           ("optional", type_string, "build_date", 2),
                           ("optional", type_double, "build_time", 3),
                           ("optional", type_string, "build_user", 4),
                           ("optional", type_string, "git_sha", 5),
                           ("optional", type_string, "git_branch", 6),
                           ("optional", type_string, "git_tag", 7)]

class ContainerStatus(Message):
    container_id = None
    network_infos = None
    cgroup_info = None
    executor_pid = None

    def __init__(self):
        self.__lookup__ = [("optional", ContainerID, "container_id", 4),
                           ("repeated", NetworkInfo, "network_infos", 1),
                           ("optional", CgroupInfo, "cgroup_info", 2),
                           ("optional", type_uint32, "executor_pid", 3)]

class CheckInfo(Message):
    class Command(Message):
        command = None

        def __init__(self):
            self.__lookup__ = [("required", CommandInfo, "command", 1)]

    class Type:
        UNKNOWN = 0
        HTTP = 2
        COMMAND = 1

    class Http(Message):
        port = None
        path = None

        def __init__(self):
            self.__lookup__ = [("required", type_uint32, "port", 1),
                               ("optional", type_string, "path", 2)]

    type = None
    command = None
    http = None
    delay_seconds = None
    interval_seconds = None
    timeout_seconds = None

    def __init__(self):
        self.__lookup__ = [("optional", type_enum, "type", 1),
                           ("optional", CheckInfo.Command, "command", 2),
                           ("optional", CheckInfo.Http, "http", 3),
                           ("optional", type_double, "delay_seconds", 4),
                           ("optional", type_double, "interval_seconds", 5),
                           ("optional", type_double, "timeout_seconds", 6)]

        self.delay_seconds = 15.0
        self.interval_seconds = 10.0
        self.timeout_seconds = 20.0

class TcpStatistics(Message):
    RtoAlgorithm = None
    RtoMin = None
    RtoMax = None
    MaxConn = None
    ActiveOpens = None
    PassiveOpens = None
    AttemptFails = None
    EstabResets = None
    CurrEstab = None
    InSegs = None
    OutSegs = None
    RetransSegs = None
    InErrs = None
    OutRsts = None
    InCsumErrors = None

    def __init__(self):
        self.__lookup__ = [("optional", type_int64, "RtoAlgorithm", 1),
                           ("optional", type_int64, "RtoMin", 2),
                           ("optional", type_int64, "RtoMax", 3),
                           ("optional", type_int64, "MaxConn", 4),
                           ("optional", type_int64, "ActiveOpens", 5),
                           ("optional", type_int64, "PassiveOpens", 6),
                           ("optional", type_int64, "AttemptFails", 7),
                           ("optional", type_int64, "EstabResets", 8),
                           ("optional", type_int64, "CurrEstab", 9),
                           ("optional", type_int64, "InSegs", 10),
                           ("optional", type_int64, "OutSegs", 11),
                           ("optional", type_int64, "RetransSegs", 12),
                           ("optional", type_int64, "InErrs", 13),
                           ("optional", type_int64, "OutRsts", 14),
                           ("optional", type_int64, "InCsumErrors", 15)]

class RateLimits(Message):
    limits = None
    aggregate_default_qps = None
    aggregate_default_capacity = None

    def __init__(self):
        self.__lookup__ = [("repeated", RateLimit, "limits", 1),
                           ("optional", type_double, "aggregate_default_qps", 2),
                           ("optional", type_uint64, "aggregate_default_capacity", 3)]

class Attribute(Message):
    name = None
    type = None
    scalar = None
    ranges = None
    set = None
    text = None

    def __init__(self):
        self.__lookup__ = [("required", type_string, "name", 1),
                           ("required", type_enum, "type", 2),
                           ("optional", Value.Scalar, "scalar", 3),
                           ("optional", Value.Ranges, "ranges", 4),
                           ("optional", Value.Set, "set", 6),
                           ("optional", Value.Text, "text", 5)]

class Image(Message):
    class Appc(Message):
        name = None
        id = None
        labels = None

        def __init__(self):
            self.__lookup__ = [("required", type_string, "name", 1),
                               ("optional", type_string, "id", 2),
                               ("optional", Labels, "labels", 3)]

    class Docker(Message):
        name = None
        credential = None

        def __init__(self):
            self.__lookup__ = [("required", type_string, "name", 1),
                               ("optional", Credential, "credential", 2)]

    class Type:
        DOCKER = 2
        APPC = 1

    type = None
    appc = None
    docker = None
    cached = None

    def __init__(self):
        self.__lookup__ = [("required", type_enum, "type", 1),
                           ("optional", Image.Appc, "appc", 2),
                           ("optional", Image.Docker, "docker", 3),
                           ("optional", type_bool, "cached", 4)]

        self.cached = True

class Labels(Message):
    labels = None

    def __init__(self):
        self.__lookup__ = [("repeated", Label, "labels", 1)]

class RLimitInfo(Message):
    class RLimit(Message):
        class Type:
            RLMT_NPROC = 11
            RLMT_MSGQUEUE = 8
            RLMT_SIGPENDING = 15
            RLMT_RTTIME = 14
            RLMT_RTPRIO = 13
            UNKNOWN = 0
            RLMT_NICE = 9
            RLMT_FSIZE = 5
            RLMT_MEMLOCK = 7
            RLMT_CORE = 2
            RLMT_LOCKS = 6
            RLMT_DATA = 4
            RLMT_NOFILE = 10
            RLMT_RSS = 12
            RLMT_STACK = 16
            RLMT_CPU = 3
            RLMT_AS = 1

        type = None
        hard = None
        soft = None

        def __init__(self):
            self.__lookup__ = [("optional", type_enum, "type", 1),
                               ("optional", type_uint64, "hard", 2),
                               ("optional", type_uint64, "soft", 3)]

    rlimits = None

    def __init__(self):
        self.__lookup__ = [("repeated", RLimitInfo.RLimit, "rlimits", 1)]

class WeightInfo(Message):
    weight = None
    role = None

    def __init__(self):
        self.__lookup__ = [("required", type_double, "weight", 1),
                           ("optional", type_string, "role", 2)]

class TrafficControlStatistics(Message):
    id = None
    backlog = None
    bytes = None
    drops = None
    overlimits = None
    packets = None
    qlen = None
    ratebps = None
    ratepps = None
    requeues = None

    def __init__(self):
        self.__lookup__ = [("required", type_string, "id", 1),
                           ("optional", type_uint64, "backlog", 2),
                           ("optional", type_uint64, "bytes", 3),
                           ("optional", type_uint64, "drops", 4),
                           ("optional", type_uint64, "overlimits", 5),
                           ("optional", type_uint64, "packets", 6),
                           ("optional", type_uint64, "qlen", 7),
                           ("optional", type_uint64, "ratebps", 8),
                           ("optional", type_uint64, "ratepps", 9),
                           ("optional", type_uint64, "requeues", 10)]

class CommandInfo(Message):
    class URI(Message):
        value = None
        executable = None
        extract = None
        cache = None
        output_file = None

        def __init__(self):
            self.__lookup__ = [("required", type_string, "value", 1),
                               ("optional", type_bool, "executable", 2),
                               ("optional", type_bool, "extract", 3),
                               ("optional", type_bool, "cache", 4),
                               ("optional", type_string, "output_file", 5)]

            self.extract = True

    uris = None
    environment = None
    shell = None
    value = None
    arguments = None
    user = None

    def __init__(self):
        self.__lookup__ = [("repeated", CommandInfo.URI, "uris", 1),
                           ("optional", Environment, "environment", 2),
                           ("optional", type_bool, "shell", 6),
                           ("optional", type_string, "value", 3),
                           ("repeated", type_string, "arguments", 7),
                           ("optional", type_string, "user", 5)]

        self.shell = True

class Unavailability(Message):
    start = None
    duration = None

    def __init__(self):
        self.__lookup__ = [("required", TimeInfo, "start", 1),
                           ("optional", DurationInfo, "duration", 2)]

class TimeInfo(Message):
    nanoseconds = None

    def __init__(self):
        self.__lookup__ = [("required", type_int64, "nanoseconds", 1)]

class PerfStatistics(Message):
    timestamp = None
    duration = None
    cycles = None
    stalled_cycles_frontend = None
    stalled_cycles_backend = None
    instructions = None
    cache_references = None
    cache_misses = None
    branches = None
    branch_misses = None
    bus_cycles = None
    ref_cycles = None
    cpu_clock = None
    task_clock = None
    page_faults = None
    minor_faults = None
    major_faults = None
    context_switches = None
    cpu_migrations = None
    alignment_faults = None
    emulation_faults = None
    l1_dcache_loads = None
    l1_dcache_load_misses = None
    l1_dcache_stores = None
    l1_dcache_store_misses = None
    l1_dcache_prefetches = None
    l1_dcache_prefetch_misses = None
    l1_icache_loads = None
    l1_icache_load_misses = None
    l1_icache_prefetches = None
    l1_icache_prefetch_misses = None
    llc_loads = None
    llc_load_misses = None
    llc_stores = None
    llc_store_misses = None
    llc_prefetches = None
    llc_prefetch_misses = None
    dtlb_loads = None
    dtlb_load_misses = None
    dtlb_stores = None
    dtlb_store_misses = None
    dtlb_prefetches = None
    dtlb_prefetch_misses = None
    itlb_loads = None
    itlb_load_misses = None
    branch_loads = None
    branch_load_misses = None
    node_loads = None
    node_load_misses = None
    node_stores = None
    node_store_misses = None
    node_prefetches = None
    node_prefetch_misses = None

    def __init__(self):
        self.__lookup__ = [("required", type_double, "timestamp", 1),
                           ("required", type_double, "duration", 2),
                           ("optional", type_uint64, "cycles", 3),
                           ("optional", type_uint64, "stalled_cycles_frontend", 4),
                           ("optional", type_uint64, "stalled_cycles_backend", 5),
                           ("optional", type_uint64, "instructions", 6),
                           ("optional", type_uint64, "cache_references", 7),
                           ("optional", type_uint64, "cache_misses", 8),
                           ("optional", type_uint64, "branches", 9),
                           ("optional", type_uint64, "branch_misses", 10),
                           ("optional", type_uint64, "bus_cycles", 11),
                           ("optional", type_uint64, "ref_cycles", 12),
                           ("optional", type_double, "cpu_clock", 13),
                           ("optional", type_double, "task_clock", 14),
                           ("optional", type_uint64, "page_faults", 15),
                           ("optional", type_uint64, "minor_faults", 16),
                           ("optional", type_uint64, "major_faults", 17),
                           ("optional", type_uint64, "context_switches", 18),
                           ("optional", type_uint64, "cpu_migrations", 19),
                           ("optional", type_uint64, "alignment_faults", 20),
                           ("optional", type_uint64, "emulation_faults", 21),
                           ("optional", type_uint64, "l1_dcache_loads", 22),
                           ("optional", type_uint64, "l1_dcache_load_misses", 23),
                           ("optional", type_uint64, "l1_dcache_stores", 24),
                           ("optional", type_uint64, "l1_dcache_store_misses", 25),
                           ("optional", type_uint64, "l1_dcache_prefetches", 26),
                           ("optional", type_uint64, "l1_dcache_prefetch_misses", 27),
                           ("optional", type_uint64, "l1_icache_loads", 28),
                           ("optional", type_uint64, "l1_icache_load_misses", 29),
                           ("optional", type_uint64, "l1_icache_prefetches", 30),
                           ("optional", type_uint64, "l1_icache_prefetch_misses", 31),
                           ("optional", type_uint64, "llc_loads", 32),
                           ("optional", type_uint64, "llc_load_misses", 33),
                           ("optional", type_uint64, "llc_stores", 34),
                           ("optional", type_uint64, "llc_store_misses", 35),
                           ("optional", type_uint64, "llc_prefetches", 36),
                           ("optional", type_uint64, "llc_prefetch_misses", 37),
                           ("optional", type_uint64, "dtlb_loads", 38),
                           ("optional", type_uint64, "dtlb_load_misses", 39),
                           ("optional", type_uint64, "dtlb_stores", 40),
                           ("optional", type_uint64, "dtlb_store_misses", 41),
                           ("optional", type_uint64, "dtlb_prefetches", 42),
                           ("optional", type_uint64, "dtlb_prefetch_misses", 43),
                           ("optional", type_uint64, "itlb_loads", 44),
                           ("optional", type_uint64, "itlb_load_misses", 45),
                           ("optional", type_uint64, "branch_loads", 46),
                           ("optional", type_uint64, "branch_load_misses", 47),
                           ("optional", type_uint64, "node_loads", 48),
                           ("optional", type_uint64, "node_load_misses", 49),
                           ("optional", type_uint64, "node_stores", 50),
                           ("optional", type_uint64, "node_store_misses", 51),
                           ("optional", type_uint64, "node_prefetches", 52),
                           ("optional", type_uint64, "node_prefetch_misses", 53)]

class NetworkInfo(Message):
    class IPAddress(Message):
        protocol = None
        ip_address = None

        def __init__(self):
            self.__lookup__ = [("optional", type_enum, "protocol", 1),
                               ("optional", type_string, "ip_address", 2)]

    class Protocol:
        IPv4 = 1
        IPv6 = 2

    class PortMapping(Message):
        host_port = None
        container_port = None
        protocol = None

        def __init__(self):
            self.__lookup__ = [("required", type_uint32, "host_port", 1),
                               ("required", type_uint32, "container_port", 2),
                               ("optional", type_string, "protocol", 3)]

    ip_addresses = None
    name = None
    groups = None
    labels = None
    port_mappings = None

    def __init__(self):
        self.__lookup__ = [("repeated", NetworkInfo.IPAddress, "ip_addresses", 5),
                           ("optional", type_string, "name", 6),
                           ("repeated", type_string, "groups", 3),
                           ("optional", Labels, "labels", 4),
                           ("repeated", NetworkInfo.PortMapping, "port_mappings", 7)]

class TaskInfo(Message):
    name = None
    task_id = None
    slave_id = None
    resources = None
    executor = None
    command = None
    container = None
    health_check = None
    check = None
    kill_policy = None
    data = None
    labels = None
    discovery = None

    def __init__(self):
        self.__lookup__ = [("required", type_string, "name", 1),
                           ("required", TaskID, "task_id", 2),
                           ("required", SlaveID, "slave_id", 3),
                           ("repeated", Resource, "resources", 4),
                           ("optional", ExecutorInfo, "executor", 5),
                           ("optional", CommandInfo, "command", 7),
                           ("optional", ContainerInfo, "container", 9),
                           ("optional", HealthCheck, "health_check", 8),
                           ("optional", CheckInfo, "check", 13),
                           ("optional", KillPolicy, "kill_policy", 12),
                           ("optional", type_bytes, "data", 6),
                           ("optional", Labels, "labels", 10),
                           ("optional", DiscoveryInfo, "discovery", 11)]

class SlaveID(Message):
    value = None

    def __init__(self):
        self.__lookup__ = [("required", type_string, "value", 1)]

class SNMPStatistics(Message):
    ip_stats = None
    icmp_stats = None
    tcp_stats = None
    udp_stats = None

    def __init__(self):
        self.__lookup__ = [("optional", IpStatistics, "ip_stats", 1),
                           ("optional", IcmpStatistics, "icmp_stats", 2),
                           ("optional", TcpStatistics, "tcp_stats", 3),
                           ("optional", UdpStatistics, "udp_stats", 4)]



class Cpus(Value.Scalar):
    name = "cpus"
    type = "SCALAR"



class Mem(Value.Scalar):
    # scalar = attr.ib(default=None,convert=lambda d: Scalar(d))
    name = "mem"
    type = "SCALAR"




class Disk(Value.Scalar):
    # scalar = attr.ib(default=None,convert=lambda d: Scalar(d))
    name = "disk"
    type = "SCALAR"
