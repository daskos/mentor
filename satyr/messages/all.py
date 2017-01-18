from __future__ import absolute_import, division, print_function

import attr



@attr.s
class Scalar(object):
    value = attr.ib()

@attr.s
class Variable(object):
    name = attr.ib()
    value = attr.ib()


@attr.s
class Environment(object):
    variables = attr.ib(convert=lambda d: Variable(**d))


@attr.s
class DiscoveryInfo(object):
    environment = attr.ib()

    labels = attr.ib(convert=lambda d: Labels(**d))

    location = attr.ib()

    name = attr.ib()

    ports = attr.ib(convert=lambda d: Ports(**d))

    version = attr.ib()

    visibility = attr.ib()


@attr.s
class Metric(object):
    name = attr.ib()

    value = attr.ib()


@attr.s
class Task(object):
    id = attr.ib(convert=lambda d: TaskID(**d))

    labels = attr.ib(convert=lambda d: Labels(**d))

    name = attr.ib()
    resources = attr.ib(convert=lambda d: Resource(**d))


@attr.s
class Executor(object):
    allocated = attr.ib(convert=lambda d: Resource(**d))

    container_id = attr.ib(convert=lambda d: ContainerID(**d))

    executor_info = attr.ib(convert=lambda d: ExecutorInfo(**d))

    statistics = attr.ib(convert=lambda d: ResourceStatistics(**d))

    tasks = attr.ib(convert=lambda d: Task(**d))


@attr.s
class ResourceUsage(object):
    executors = attr.ib(convert=lambda d: Executor(**d))

    total = attr.ib(convert=lambda d: Resource(**d))


@attr.s
class VersionInfo(object):
    build_date = attr.ib()

    build_time = attr.ib()

    build_user = attr.ib()

    git_branch = attr.ib()

    git_sha = attr.ib()

    git_tag = attr.ib()

    version = attr.ib()


@attr.s
class IpStatistics(object):
    DefaultTTL = attr.ib()

    ForwDatagrams = attr.ib()

    Forwarding = attr.ib()

    FragCreates = attr.ib()

    FragFails = attr.ib()

    FragOKs = attr.ib()

    InAddrErrors = attr.ib()

    InDelivers = attr.ib()

    InDiscards = attr.ib()

    InHdrErrors = attr.ib()

    InReceives = attr.ib()

    InUnknownProtos = attr.ib()

    OutDiscards = attr.ib()

    OutNoRoutes = attr.ib()

    OutRequests = attr.ib()

    ReasmFails = attr.ib()

    ReasmOKs = attr.ib()

    ReasmReqds = attr.ib()

    ReasmTimeout = attr.ib()


@attr.s
class RateLimits(object):
    aggregate_default_capacity = attr.ib()

    aggregate_default_qps = attr.ib()

    limits = attr.ib(convert=lambda d: RateLimit(**d))


@attr.s
class DurationInfo(object):
    nanoseconds = attr.ib()


@attr.s
class Offer(object):
    attributes = attr.ib(convert=lambda d: Attribute(**d))

    executor_ids = attr.ib(convert=lambda d: ExecutorID(**d))

    framework_id = attr.ib(convert=lambda d: FrameworkID(**d))

    hostname = attr.ib()

    id = attr.ib(convert=lambda d: OfferID(**d))

    resources = attr.ib(convert=lambda d: Resource(**d))

    slave_id = attr.ib(convert=lambda d: SlaveID(**d))

    unavailability = attr.ib(convert=lambda d: Unavailability(**d))

    url = attr.ib(convert=lambda d: URL(**d))


@attr.s
class TCPCheckInfo(object):
    port = attr.ib()


@attr.s
class HTTPCheckInfo(object):
    port = attr.ib()


@attr.s
class HealthCheck(object):
    command = attr.ib(convert=lambda d: CommandInfo(**d))

    consecutive_failures = attr.ib()

    delay_seconds = attr.ib()

    grace_period_seconds = attr.ib()

    http = attr.ib(convert=lambda d: HTTPCheckInfo(**d))

    interval_seconds = attr.ib()

    tcp = attr.ib(convert=lambda d: TCPCheckInfo(**d))

    timeout_seconds = attr.ib()

    type = attr.ib()


@attr.s
class Port(object):
    labels = attr.ib(convert=lambda d: Labels(**d))

    name = attr.ib()

    number = attr.ib()

    protocol = attr.ib()

    visibility = attr.ib()


@attr.s
class PerfStatistics(object):
    alignment_faults = attr.ib()

    branch_load_misses = attr.ib()

    branch_loads = attr.ib()

    branch_misses = attr.ib()

    branches = attr.ib()

    bus_cycles = attr.ib()

    cache_misses = attr.ib()

    cache_references = attr.ib()

    context_switches = attr.ib()

    cpu_clock = attr.ib()

    cpu_migrations = attr.ib()

    cycles = attr.ib()

    dtlb_load_misses = attr.ib()

    dtlb_loads = attr.ib()

    dtlb_prefetch_misses = attr.ib()

    dtlb_prefetches = attr.ib()

    dtlb_store_misses = attr.ib()

    dtlb_stores = attr.ib()

    duration = attr.ib()

    emulation_faults = attr.ib()

    instructions = attr.ib()

    itlb_load_misses = attr.ib()

    itlb_loads = attr.ib()

    l1_dcache_load_misses = attr.ib()

    l1_dcache_loads = attr.ib()

    l1_dcache_prefetch_misses = attr.ib()

    l1_dcache_prefetches = attr.ib()

    l1_dcache_store_misses = attr.ib()

    l1_dcache_stores = attr.ib()

    l1_icache_load_misses = attr.ib()

    l1_icache_loads = attr.ib()

    l1_icache_prefetch_misses = attr.ib()

    l1_icache_prefetches = attr.ib()

    llc_load_misses = attr.ib()

    llc_loads = attr.ib()

    llc_prefetch_misses = attr.ib()

    llc_prefetches = attr.ib()

    llc_store_misses = attr.ib()

    llc_stores = attr.ib()

    major_faults = attr.ib()

    minor_faults = attr.ib()

    node_load_misses = attr.ib()

    node_loads = attr.ib()

    node_prefetch_misses = attr.ib()

    node_prefetches = attr.ib()

    node_store_misses = attr.ib()

    node_stores = attr.ib()

    page_faults = attr.ib()

    ref_cycles = attr.ib()

    stalled_cycles_backend = attr.ib()

    stalled_cycles_frontend = attr.ib()

    task_clock = attr.ib()

    timestamp = attr.ib()


@attr.s
class TcpStatistics(object):
    ActiveOpens = attr.ib()

    AttemptFails = attr.ib()

    CurrEstab = attr.ib()

    EstabResets = attr.ib()

    InCsumErrors = attr.ib()

    InErrs = attr.ib()

    InSegs = attr.ib()

    MaxConn = attr.ib()

    OutRsts = attr.ib()

    OutSegs = attr.ib()

    PassiveOpens = attr.ib()

    RetransSegs = attr.ib()

    RtoAlgorithm = attr.ib()

    RtoMax = attr.ib()

    RtoMin = attr.ib()


@attr.s
class URL(object):
    address = attr.ib(convert=lambda d: Address(**d))

    fragment = attr.ib()

    path = attr.ib()

    query = attr.ib(convert=lambda d: Parameter(**d))

    scheme = attr.ib()


@attr.s
class FileInfo(object):
    gid = attr.ib()

    mode = attr.ib()

    mtime = attr.ib(convert=lambda d: TimeInfo(**d))

    nlink = attr.ib()

    path = attr.ib()

    size = attr.ib()

    uid = attr.ib()


@attr.s
class IPAddress(object):
    protocol = attr.ib()
    ip_address = attr.ib()


@attr.s
class PortMapping(object):
    container_port = attr.ib()

    host_port = attr.ib()

    protocol = attr.ib()


@attr.s
class NetworkInfo(object):
    groups = attr.ib()

    ip_addresses = attr.ib(convert=lambda d: IPAddress(**d))

    labels = attr.ib(convert=lambda d: Labels(**d))

    name = attr.ib()

    port_mappings = attr.ib(convert=lambda d: PortMapping(**d))


@attr.s
class MasterInfo(object):
    address = attr.ib(convert=lambda d: Address(**d))

    hostname = attr.ib()

    id = attr.ib()

    ip = attr.ib()

    pid = attr.ib()

    port = attr.ib()

    version = attr.ib()


@attr.s
class Unavailability(object):
    duration = attr.ib(convert=lambda d: DurationInfo(**d))

    start = attr.ib(convert=lambda d: TimeInfo(**d))


@attr.s
class InverseOffer(object):
    framework_id = attr.ib(convert=lambda d: FrameworkID(**d))

    id = attr.ib(convert=lambda d: OfferID(**d))

    resources = attr.ib(convert=lambda d: Resource(**d))

    slave_id = attr.ib(convert=lambda d: SlaveID(**d))

    unavailability = attr.ib(convert=lambda d: Unavailability(**d))

    url = attr.ib(convert=lambda d: URL(**d))


@attr.s
class Capability(object):
    type = attr.ib()


@attr.s
class FrameworkInfo(object):
    capabilities = attr.ib(convert=lambda d: Capability(**d))

    checkpoint = attr.ib()

    failover_timeout = attr.ib()

    hostname = attr.ib()

    id = attr.ib(convert=lambda d: FrameworkID(**d))

    labels = attr.ib(convert=lambda d: Labels(**d))

    name = attr.ib()

    principal = attr.ib()

    role = attr.ib()

    user = attr.ib()

    webui_url = attr.ib()


@attr.s
class Labels(object):
    labels = attr.ib(convert=lambda d: Label(**d))


@attr.s
class NetCls(object):
    classid = attr.ib()


@attr.s
class CgroupInfo(object):
    net_cls = attr.ib(convert=lambda d: NetCls(**d))


@attr.s
class TaskStatus(object):
    container_status = attr.ib(convert=lambda d: ContainerStatus(**d))

    data = attr.ib()

    executor_id = attr.ib(convert=lambda d: ExecutorID(**d))

    healthy = attr.ib()

    labels = attr.ib(convert=lambda d: Labels(**d))

    message = attr.ib()

    reason = attr.ib()

    slave_id = attr.ib(convert=lambda d: SlaveID(**d))

    source = attr.ib()

    state = attr.ib()

    task_id = attr.ib(convert=lambda d: TaskID(**d))

    timestamp = attr.ib()

    unreachable_time = attr.ib(convert=lambda d: TimeInfo(**d))

    uuid = attr.ib()


@attr.s
class SNMPStatistics(object):
    icmp_stats = attr.ib(convert=lambda d: IcmpStatistics(**d))

    ip_stats = attr.ib(convert=lambda d: IpStatistics(**d))

    tcp_stats = attr.ib(convert=lambda d: TcpStatistics(**d))

    udp_stats = attr.ib(convert=lambda d: UdpStatistics(**d))


@attr.s
class WeightInfo(object):
    role = attr.ib()

    weight = attr.ib()


@attr.s
class Parameter(object):
    key = attr.ib()

    value = attr.ib()


@attr.s
class TrafficControlStatistics(object):
    backlog = attr.ib()

    bytes = attr.ib()

    drops = attr.ib()

    id = attr.ib()

    overlimits = attr.ib()

    packets = attr.ib()

    qlen = attr.ib()

    ratebps = attr.ib()

    ratepps = attr.ib()

    requeues = attr.ib()


@attr.s
class TaskInfo(object):
    command = attr.ib(convert=lambda d: CommandInfo(**d))

    container = attr.ib(convert=lambda d: ContainerInfo(**d))

    data = attr.ib()

    discovery = attr.ib(convert=lambda d: DiscoveryInfo(**d))

    executor = attr.ib(convert=lambda d: ExecutorInfo(**d))

    health_check = attr.ib(convert=lambda d: HealthCheck(**d))

    kill_policy = attr.ib(convert=lambda d: KillPolicy(**d))

    labels = attr.ib(convert=lambda d: Labels(**d))

    name = attr.ib()

    resources = attr.ib(convert=lambda d: Resource(**d))

    slave_id = attr.ib(convert=lambda d: SlaveID(**d))

    task_id = attr.ib(convert=lambda d: TaskID(**d))


@attr.s
class Request(object):
    resources = attr.ib(convert=lambda d: Resource(**d))

    slave_id = attr.ib(convert=lambda d: SlaveID(**d))


@attr.s
class LinuxInfo(object):
    capability_info = attr.ib(convert=lambda d: CapabilityInfo(**d))


@attr.s
class ExecutorInfo(object):
    command = attr.ib(convert=lambda d: CommandInfo(**d))

    container = attr.ib(convert=lambda d: ContainerInfo(**d))

    data = attr.ib()

    discovery = attr.ib(convert=lambda d: DiscoveryInfo(**d))

    executor_id = attr.ib(convert=lambda d: ExecutorID(**d))

    framework_id = attr.ib(convert=lambda d: FrameworkID(**d))

    labels = attr.ib(convert=lambda d: Labels(**d))

    name = attr.ib()

    resources = attr.ib(convert=lambda d: Resource(**d))

    shutdown_grace_period = attr.ib(convert=lambda d: DurationInfo(**d))

    source = attr.ib()

    type = attr.ib()


@attr.s
class Filters(object):
    refuse_seconds = attr.ib()


@attr.s
class Flag(object):
    name = attr.ib()

    value = attr.ib()


@attr.s
class UdpStatistics(object):
    IgnoredMulti = attr.ib()

    InCsumErrors = attr.ib()

    InDatagrams = attr.ib()

    InErrors = attr.ib()

    NoPorts = attr.ib()

    OutDatagrams = attr.ib()

    RcvbufErrors = attr.ib()

    SndbufErrors = attr.ib()


@attr.s
class Mount(object):
    root = attr.ib()


@attr.s
class Path(object):
    root = attr.ib()


@attr.s
class Persistence(object):
    id = attr.ib()

    principal = attr.ib()


@attr.s
class Source(object):
    mount = attr.ib(convert=lambda d: Mount(**d))

    path = attr.ib(convert=lambda d: Path(**d))

    type = attr.ib()


@attr.s
class ReservationInfo(object):
    labels = attr.ib(convert=lambda d: Labels(**d))

    principal = attr.ib()


@attr.s
class DiskInfo(object):
    persistence = attr.ib(convert=lambda d: Persistence(**d))

    source = attr.ib(convert=lambda d: Source(**d))

    volume = attr.ib(convert=lambda d: Volume(**d))

@attr.s
class Cpus(object):
    scalar = attr.ib(convert=lambda d: Scalar(d))
    name = "cpus"
    type= "SCALAR"


@attr.s
class Mem(object):
    scalar = attr.ib(convert=lambda d: Scalar(d))
    name = "mem"
    type = "SCALAR"


@attr.s
class Disk(object):
    scalar = attr.ib(convert=lambda d: Scalar(d))
    name = "disk"
    type = "SCALAR"


@attr.s
class Resource(object):
    disk = attr.ib(convert=lambda d: DiskInfo(**d))

    name = attr.ib()

    ranges = attr.ib(convert=lambda d: Ranges(**d))

    reservation = attr.ib(convert=lambda d: ReservationInfo(**d))

    revocable = attr.ib()

    role = attr.ib()

    scalar = attr.ib(convert=lambda d: Scalar(**d))

    set = attr.ib(convert=lambda d: Set(**d))

    shared = attr.ib()

    type = attr.ib()


@attr.s
class ExecutorID(object):
    value = attr.ib()


@attr.s
class Set(object):
    item = attr.ib()


@attr.s
class Ranges(object):
    range = attr.ib(convert=lambda d: Range(**d))




@attr.s
class Range(object):
    begin = attr.ib()

    end = attr.ib()


@attr.s
class Text(object):
    value = attr.ib()


@attr.s
class Attribute(object):
    name = attr.ib()

    ranges = attr.ib(convert=lambda d: Ranges(**d))

    scalar = attr.ib(convert=lambda d: Scalar(**d))

    set = attr.ib(convert=lambda d: Set(**d))

    text = attr.ib(convert=lambda d: Text(**d))

    type = attr.ib()


@attr.s
class Volume(object):
    container_path = attr.ib()

    host_path = attr.ib()

    image = attr.ib(convert=lambda d: Image(**d))

    mode = attr.ib()

    source = attr.ib(convert=lambda d: Source(**d))


@attr.s
class ContainerStatus(object):
    cgroup_info = attr.ib(convert=lambda d: CgroupInfo(**d))

    executor_pid = attr.ib()

    network_infos = attr.ib(convert=lambda d: NetworkInfo(**d))


@attr.s
class SlaveInfo(object):
    attributes = attr.ib(convert=lambda d: Attribute(**d))

    checkpoint = attr.ib()

    hostname = attr.ib()

    id = attr.ib(convert=lambda d: SlaveID(**d))

    port = attr.ib()

    resources = attr.ib(convert=lambda d: Resource(**d))


@attr.s
class CommandInfo(object):
    arguments = attr.ib()

    environment = attr.ib(convert=lambda d: Environment(**d))

    shell = attr.ib()

    uris = attr.ib(convert=lambda d: URI(**d))

    user = attr.ib()

    value = attr.ib()


@attr.s
class Appc(object):
    id = attr.ib()

    labels = attr.ib(convert=lambda d: Labels(**d))

    name = attr.ib()


@attr.s
class Docker(object):
    credential = attr.ib(convert=lambda d: Credential(**d))

    name = attr.ib()


@attr.s
class Image(object):
    appc = attr.ib(convert=lambda d: Appc(**d))

    cached = attr.ib()

    docker = attr.ib(convert=lambda d: Docker(**d))

    type = attr.ib()


@attr.s
class URI(object):
    cache = attr.ib()

    executable = attr.ib()

    extract = attr.ib()

    output_file = attr.ib()

    value = attr.ib()


@attr.s
class ResourceStatistics(object):
    cpus_limit = attr.ib()

    cpus_nr_periods = attr.ib()

    cpus_nr_throttled = attr.ib()

    cpus_system_time_secs = attr.ib()

    cpus_throttled_time_secs = attr.ib()

    cpus_user_time_secs = attr.ib()

    disk_limit_bytes = attr.ib()

    disk_used_bytes = attr.ib()

    mem_anon_bytes = attr.ib()

    mem_cache_bytes = attr.ib()

    mem_critical_pressure_counter = attr.ib()

    mem_file_bytes = attr.ib()

    mem_limit_bytes = attr.ib()

    mem_low_pressure_counter = attr.ib()

    mem_mapped_file_bytes = attr.ib()

    mem_medium_pressure_counter = attr.ib()

    mem_rss_bytes = attr.ib()

    mem_soft_limit_bytes = attr.ib()

    mem_swap_bytes = attr.ib()

    mem_total_bytes = attr.ib()

    mem_total_memsw_bytes = attr.ib()

    mem_unevictable_bytes = attr.ib()

    net_rx_bytes = attr.ib()

    net_rx_dropped = attr.ib()

    net_rx_errors = attr.ib()

    net_rx_packets = attr.ib()

    net_snmp_statistics = attr.ib(convert=lambda d: SNMPStatistics(**d))

    net_tcp_active_connections = attr.ib()

    net_tcp_rtt_microsecs_p50 = attr.ib()

    net_tcp_rtt_microsecs_p90 = attr.ib()

    net_tcp_rtt_microsecs_p95 = attr.ib()

    net_tcp_rtt_microsecs_p99 = attr.ib()

    net_tcp_time_wait_connections = attr.ib()

    net_traffic_control_statistics = attr.ib(convert=lambda d: TrafficControlStatistics(**d))

    net_tx_bytes = attr.ib()

    net_tx_dropped = attr.ib()

    net_tx_errors = attr.ib()

    net_tx_packets = attr.ib()

    perf = attr.ib(convert=lambda d: PerfStatistics(**d))

    processes = attr.ib()

    threads = attr.ib()

    timestamp = attr.ib()


@attr.s
class IcmpStatistics(object):
    InAddrMaskReps = attr.ib()

    InAddrMasks = attr.ib()

    InCsumErrors = attr.ib()

    InDestUnreachs = attr.ib()

    InEchoReps = attr.ib()

    InEchos = attr.ib()

    InErrors = attr.ib()

    InMsgs = attr.ib()

    InParmProbs = attr.ib()

    InRedirects = attr.ib()

    InSrcQuenchs = attr.ib()

    InTimeExcds = attr.ib()

    InTimestampReps = attr.ib()

    InTimestamps = attr.ib()

    OutAddrMaskReps = attr.ib()

    OutAddrMasks = attr.ib()

    OutDestUnreachs = attr.ib()

    OutEchoReps = attr.ib()

    OutEchos = attr.ib()

    OutErrors = attr.ib()

    OutMsgs = attr.ib()

    OutParmProbs = attr.ib()

    OutRedirects = attr.ib()

    OutSrcQuenchs = attr.ib()

    OutTimeExcds = attr.ib()

    OutTimestampReps = attr.ib()

    OutTimestamps = attr.ib()


@attr.s
class TaskGroupInfo(object):
    tasks = attr.ib(convert=lambda d: TaskInfo(**d))


@attr.s
class RateLimit(object):
    capacity = attr.ib()

    principal = attr.ib()

    qps = attr.ib()


@attr.s
class Value(object):
    ranges = attr.ib(convert=lambda d: Ranges(**d))

    scalar = attr.ib(convert=lambda d: Scalar(**d))

    set = attr.ib(convert=lambda d: Set(**d))

    text = attr.ib(convert=lambda d: Text(**d))

    type = attr.ib()


@attr.s
class OfferID(object):
    value = attr.ib()


@attr.s
class Ports(object):
    ports = attr.ib(convert=lambda d: Port(**d))


@attr.s
class SlaveID(object):
    value = attr.ib()



@attr.s
class ContainerInfo(object):
    @attr.s
    class DockerInfo(object):
        force_pull_image = attr.ib()

        image = attr.ib()

        network = attr.ib()

        parameters = attr.ib(convert=lambda d: Parameter(**d))

        port_mappings = attr.ib(convert=lambda d: PortMapping(**d))

        privileged = attr.ib()

        volume_driver = attr.ib()

    @attr.s
    class MesosInfo(object):
        image = attr.ib(convert=lambda d: Image(**d))


    docker = attr.ib(convert=lambda d: DockerInfo(**d))

    hostname = attr.ib()

    linux_info = attr.ib(convert=lambda d: LinuxInfo(**d))

    mesos = attr.ib(convert=lambda d: MesosInfo(**d))

    network_infos = attr.ib(convert=lambda d: NetworkInfo(**d))

    type = attr.ib()

    volumes = attr.ib(convert=lambda d: Volume(**d))


@attr.s
class KillPolicy(object):
    grace_period = attr.ib(convert=lambda d: DurationInfo(**d))


@attr.s
class Address(object):
    hostname = attr.ib()

    ip = attr.ib()

    port = attr.ib()


@attr.s
class CapabilityInfo(object):
    capabilities = attr.ib()


@attr.s
class MachineID(object):
    hostname = attr.ib()

    ip = attr.ib()


@attr.s
class TimeInfo(object):
    nanoseconds = attr.ib()


@attr.s
class MachineInfo(object):
    id = attr.ib(convert=lambda d: MachineID(**d))

    mode = attr.ib()

    unavailability = attr.ib(convert=lambda d: Unavailability(**d))


@attr.s
class Parameters(object):
    parameter = attr.ib(convert=lambda d: Parameter(**d))


@attr.s
class Task(object):
    container = attr.ib(convert=lambda d: ContainerInfo(**d))

    discovery = attr.ib(convert=lambda d: DiscoveryInfo(**d))

    executor_id = attr.ib(convert=lambda d: ExecutorID(**d))

    framework_id = attr.ib(convert=lambda d: FrameworkID(**d))

    labels = attr.ib(convert=lambda d: Labels(**d))

    name = attr.ib()

    resources = attr.ib(convert=lambda d: Resource(**d))

    slave_id = attr.ib(convert=lambda d: SlaveID(**d))

    state = attr.ib()

    status_update_state = attr.ib()

    status_update_uuid = attr.ib()

    statuses = attr.ib(convert=lambda d: TaskStatus(**d))

    task_id = attr.ib(convert=lambda d: TaskID(**d))

    user = attr.ib()


@attr.s
class ContainerID(object):
    parent = attr.ib(convert=lambda d: ContainerID(**d))

    value = attr.ib()


@attr.s
class Label(object):
    key = attr.ib()

    value = attr.ib()


@attr.s
class Credentials(object):
    credentials = attr.ib(convert=lambda d: Credential(**d))


@attr.s
class Role(object):
    frameworks = attr.ib(convert=lambda d: FrameworkID(**d))

    name = attr.ib()

    resources = attr.ib(convert=lambda d: Resource(**d))

    weight = attr.ib()


@attr.s
class FrameworkID(object):
    value = attr.ib()


@attr.s
class TaskID(object):
    value = attr.ib()


@attr.s
class Credential(object):
    principal = attr.ib()
    secret = attr.ib()