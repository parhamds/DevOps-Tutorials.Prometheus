# Prometheus Cheat Sheet

This README provides a comprehensive cheat sheet for working with Prometheus, covering various commands, functions, and helpful resources.

## Docker Setup

To set up Prometheus using Docker, run the following command:

```bash
docker run -d --name prometheus-container -e TZ=UTC -p 9090:9090 -v <path_to_prometheus.yml>:/etc/prometheus/prometheus.yml -v <path_to_alerts.yml>:/etc/prometheus/alerts.yml ubuntu/prometheus
```

Access Prometheus dashboard at `localhost:9090` in your browser.

## List of Targets

```promql
up
```

Output:
```
up{instance="localhost:9090", job="prometheus"}
```

## Filter Output

```promql
process_cpu_seconds_total{instance="localhost:9090", job="prometheus"}
```

Regex Matcher:
```promql
process_cpu_seconds_total{instance="localhost:9090", job=~"promet.*"}
```

## Show Samples

```promql
process_cpu_seconds_total{instance="localhost:9090", job=~"promet.*"}[1m]
```

## Boolean Operations

```promql
prometheus_http_requests_total and promhttp_metric_handler_requests_total
```

## Ignoring Keys

```promql
prometheus_http_requests_total and ignoring(handler) promhttp_metric_handler_requests_total
```

## Operators

Find a list of operators [here](https://prometheus.io/docs/prometheus/latest/querying/operators/).

## Rate Function

```promql
rate(prometheus_http_requests_total[1m])
```

## Predict Function

```promql
predict_linear(...[1h], 2*60*60)
```

## Aggregation Operators

```promql
max_over_time(...[1h])
min_over_time
sum_over_time
```

## Sorting Output

```promql
sort(...)
sort_desc(...)
```

## Time Functions

```promql
time()
day_of_week()
day_of_month()
```

## Uptime of a Process

```promql
time() - <start_time_metric>
```

## Reloading Prometheus Config

### Method 1: Using SIGHUP Signal

```bash
ps ax | grep prometheus
kill -HUP <pid>
```

### Method 2: Using HTTP

Ensure `--web.enable-lifecycle` is enabled:
```bash
./prometheus --web.enable-lifecycle
```
or
```bash
sudo docker run -p 9090:9090 -d -v /Users/parham/Desktop/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus \
--web.enable-lifecycle \
--config.file=/etc/prometheus/prometheus.yml \
--storage.tsdb.path=/prometheus \
--web.console.libraries=/usr/share/prometheus/console_libraries --web.console.templates=/usr/share/prometheus/consoles
```

Then, reload the config:
```bash
curl -X POST http://localhost:9090/-/reload
```

# Prometheus Setup and Usage Guide

This comprehensive guide provides instructions and examples for setting up Prometheus, configuring rules and alerts, integrating with Alertmanager, and utilizing various features for monitoring and alerting. Follow the steps below to effectively utilize Prometheus in your environment.

## Rules Validation

To validate rules defined in `rules.yml`, follow these steps:

1. Download `promtool` from the Prometheus compressed package.
2. Run the validation command:

```bash
./promtool check rules <path_to_rules.yml>
```

## Rules Configuration

To create and manage rules, follow these guidelines:

1. Create a `rules.yml` file.
2. Add the file path to `prometheus.yml` under `rule_files`:

```yaml
rule_files:
  - "rules/rules.yml"
```

3. The rules will be automatically executed based on the `evaluation_interval` defined in `prometheus.yml`.
4. Reload Prometheus to apply changes.

## Alerts Configuration

Alerts can be configured in `rules.yml` or other files. Follow these steps:

1. Create alerts in `rules.yaml` or other files.
2. Add the file path to `prometheus.yml` under `rule_files`.
3. Reload Prometheus to apply changes.
4. View alerts in the Alerts tab of Prometheus. Inactive alerts are marked as "OK" while firing alerts indicate triggered conditions. You can also query alerts using `ALERTS` in Prometheus.

## Pending Alerts and `for` Clause

When using the `for` clause in alerts, pending alerts are triggered if the condition becomes true, but transitions to firing state only if the condition remains true for the specified duration. This prevents triggering alerts for temporary infrastructure issues.

## Alertmanager Setup

To set up Alertmanager, execute the following Docker command:

```bash
docker run \
--detach \
--name=alertmanager \
--volume=${PWD}:/rules.yml:/etc/alertmanager/rules.yml \
--publish=9093:9093 \
prom/alertmanager
```

1. Add the Alertmanager address (e.g., `localhost:9093`) to `prometheus.yml`.
2. Reload Prometheus to apply changes.
3. Access Alertmanager via the web interface (`localhost:9093`).

## Alert Expression Examples

Below are examples of alert expressions for Linux and Windows systems:

- Node status:
```promql
alert: NodeExporterDown
up{job="node_exporter"} == 0
```

- Memory usage:
```promql
alert: NodeMemoryUsageAbove60%
expr: 60 < (100 - job:node_memory_Mem_bytes:available) < 75
```

- CPU usage:
```promql
alert: NodeCPUUsageHigh
expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[1m])) * 100) > 80
```

## Labels and Annotations in Alerts

Labels are used to route alerts to specific receivers, while annotations provide additional information. Example:

```yaml
labels:
  severity: critical
  app_type: go

annotations:
  summary: 'Go app latency is over 5 seconds.'
  description: 'App latency of instance {{ $labels.instance }} of job {{ $labels.job }} is {{ $value }} for more than 5 minutes.'
  app_link: 'http://localhost:8000/'
```

## Stress Testing and File Creation

- Linux stress test:
```bash
sudo apt install stress-ng
stress-ng -c 2 -v --vm-bytes $(awk '/MemAvailable/{printf "%d\n", $2 * 0.85;}' < /proc/meminfo)k --vm-keep -m 1 --timeout 300s
```

- Create a file with arbitrary size in Linux:
```bash
fallocate -l 15G temp_file
```

## Alerts Configuration Validation

To validate `alerts.yml`, follow these steps:

1. Download `amtool` from the Alertmanager compressed package.
2. Run the validation command:

```bash
./amtool check-config <path_to_rules.yml>
```

## Routing Tree Link

Use the [routing tree editor](https://prometheus.io/webtools/alerting/routing-tree-editor/) to test alert routing by pasting `alerts.yml` and entering labels.

## Alertmanager Configuration

Configure Alertmanager receivers and routes in `alertmanager.yml`. Example configurations for Slack and PagerDuty integration are provided.

## Silence Rules

Use silence rules to suppress alerts during maintenance or other activities. Silence alerts in Alertmanager's web interface by creating a new silence or clicking the silence button for specific alerts.


# Blackbox Exporter Setup Guide

The Blackbox Exporter allows you to gather information from targets, such as HTTP response, TCP ports, ICMP replies, and DNS resolution, and convert them into Prometheus metrics for monitoring. Follow these steps to set up and utilize the Blackbox Exporter effectively.

## Running Blackbox Exporter

Execute the following Docker command to run the Blackbox Exporter:

```bash
docker run -d -v /Users/parham/Desktop/blackbox.yml:/etc/blackbox_exporter/config.yml -p 9115:9115 prom/blackbox-exporter-linux-arm64
```

- Access metrics of Blackbox Exporter at `/metrics`.
- Probe specific targets using the `/probe` endpoint.

## Adding Modules

### HTTP IPv4 Module

Add the IPv4 module to `blackbox.yml`:

```yaml
modules:
  http_ipv4:
    prober: http
    http:
      preferred_ip_protocol: ip4
```

Probe HTTP targets with IPv4 protocol. For example:

```text
http://localhost:9115/probe?target=prometheus.io&module=http_ipv4&debug=true
```

### Custom Module for Finding a Word in HTTP Response

Define a custom module to check if the HTTP response contains a specific word (e.g., "monitoring"):

```yaml
http_find_prom:
  prober: http
  http:
    preferred_ip_protocol: ip4
    fail_if_body_not_matches_regexp:
    - "monitoring"
```

Probe targets using this module:

```text
http://localhost:9115/probe?target=prometheus.io&module=http_find_prom
```

### TCP Connect Module

Probe if a specific port is open on an address:

```text
http://localhost:9115/probe?target=localhost:8000&module=tcp_connect
```

### ICMP Module

Check if an address responds to ICMP ping:

```yaml
modules:
  icmp:
    prober: icmp
    icmp:
      preferred_ip_protocol: ip4
```

Probe targets using ICMP module:

```text
http://localhost:9115/probe?target=prometheus.io&module=icmp
```

### DNS Module

Resolve a name on DNS to check if DNS is working:

```yaml
modules:
  dns_example:
    prober: dns
    dns:
      transport_protocol: "tcp"
      preferred_ip_protocol: ip4
      query_name: "www.google.com"
```

Probe targets using DNS module:

```text
http://localhost:9115/probe?target=8.8.8.8&module=dns_example
```

## Integrating Blackbox Exporter with Prometheus

Add the Blackbox Exporter to Prometheus configuration (`prometheus.yml`):

```yaml
- job_name: 'blackbox_exporter'
  static_configs:
  - targets: ['localhost:9115']

- job_name: 'prometheus-website'
  static_configs:
  - targets:
    - prometheus.io
  metrics_path: /probe
  params:
    module:
    - http_ipv4
  relabel_configs:
    - source_labels: [__address__]
      target_label: __param_target
    - source_labels: [__param_target]
      target_label: instance
    - target_label: __address__
      replacement: localhost:9115
```

Access Prometheus console and run queries based on Blackbox metrics.


# Pushgateway Setup Guide

The Pushgateway serves as an intermediary for batch jobs that start and finish quickly. In such scenarios, Prometheus may miss metrics if it tries to pull them directly. Instead, batch jobs push their metrics to the Pushgateway, allowing Prometheus to pull these metrics from the Pushgateway on its interval. Follow these steps to set up and utilize the Pushgateway effectively.

## Running Pushgateway

Execute the following Docker command to run the Pushgateway:

```bash
docker run -d -p 9091:9091 prom/pushgateway
```

## Pushgateway Integration with Prometheus

Integrate the Pushgateway with Prometheus by adding its address as a new job in `prometheus.yml`:

```yaml
- job_name: 'prometheus-website'
  static_configs:
  - targets:
    - prometheus.io
```

## Pushing Metrics

Push metrics to the Pushgateway using the following command:

```bash
echo "demo_metric 123" | curl --data-binary @- http://localhost:9091/metrics/job/demo_pg_job/instance/demo_instance/event/add
```

To specify custom labels for the metric, use:

```bash
echo "<metric_name> <metric_value>" | curl --data-binary @- http://localhost:9091/metrics/<label0_name>/<label0_value>/<label1_name>/<label1_value>/<label2_name>/<label2_value>
```

## Viewing Metrics in Prometheus

The pushed metrics can be viewed in Prometheus. For example, if you push a metric named `demo_metric`, you can find it in Prometheus:

```text
demo_metric{event="add", exported_instance="demo_instance", exported_job="demo_pg_job", instance="localhost:9091", job="pushgateway"}
```

By default, labels are duplicated because the default label keys are used alongside custom labels. To replace custom labels with default ones, use `honor_labels` in `prometheus.yml`:

```yaml
- job_name: 'prometheus-website'
  honor_labels: true
  static_configs:
  - targets:
    - prometheus.io
```

With this configuration, the output will be:

```text
demo_metric{event="add", instance="demo_instance", job ="demo_pg_job"}
```

## Pushing Metrics Using Cron Job

You can push metrics to the Pushgateway using a cron job. Edit the cron job configuration using:

```bash
crontab -e
```

Add the following line to push metrics every minute:

```bash
* * * * * /bin/echo "demo_metric 123" | curl --data-binary @- http://localhost:9091/metrics/job/demo_pg_job/instance/demo_instance/event/add
```

Explore [cron job examples](https://crontab.guru/examples.html) for more options and configurations.


# Service Discovery Setup Guide

Service discovery enables Prometheus targets to be dynamic, which is particularly useful in environments where targets change frequently, such as cloud environments. With service discovery, there's no need to restart Prometheus whenever there's a change in targets. Explore two methods for implementing service discovery: file-based service discovery and AWS integration.

## File-Based Service Discovery

1. **Create a file**: Generate a `file_sd.yml` or `file_sd.json` file on the Prometheus machine and define the targets within it:

    ```yaml
    - targets:
      - localhost:9100
      labels:
        team: "development"
        region: "Mumbai"
    ```

2. **Modify Prometheus Configuration**: Change a job from static configuration to use file-based service discovery in `prometheus.yml`:

    ```yaml
    - job_name: 'node_exporter'
      file_sd_configs:
      - files:
        - file_sd.yml
    ```

   Now, any changes in the file-based service discovery will be automatically applied to Prometheus without the need for manual reloads.

## AWS Integration

1. **AWS Setup**:
   - Create a user on AWS with appropriate permissions (e.g., `EC2ReadOnlyAccess`) and note down the access key ID and secret access key.

2. **Prometheus Configuration**:
   Create an EC2 job in `prometheus.yml`:

    ```yaml
    - job_name: 'ec2'
      ec2_sd_configs:
        - access_key: AKIA4EF4JNMSKSQSXYYC
          secret_key: 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
          region: ap-south-1
      relabel_configs:
        - source_labels: [__meta_ec2_public_ip]
          regex: '(.*)'
          replacement: '${1}:9100'
          target_label: __address__
    ```

3. **AWS Configuration**:
   - Create an EC2 instance and allow TCP 9100 from anywhere (or from the Prometheus server) in its security group.
   - SSH into the EC2 instance:

    ```bash
    sudo chmod 400 <sshkey.pem>
    ssh -i <sshkey.pem> ubuntu@<pub_ip_of_ec2>
    ```

4. **Install Node Exporter**:
   Install Prometheus Node Exporter on the EC2 instance:

    ```bash
    sudo apt update
    sudo apt install prometheus-node-exporter
    systemctl status prometheus-node-exporter
    ```

   Now, the EC2 instance and its metrics will be visible on Prometheus.

## Keep and Drop

To track only specific instances with specific labels, use `keep` and `drop` actions in relabeling configurations. For example, to track only instances with certain labels:

```yaml
- job_name: 'node_exporter'
  file_sd_configs:
  - files:
    - file_sd.yml
  relabel_configs:
    - source_labels: [team]
      regex: deployment|l1
      action: keep
```

This configuration ensures that only instances with the `team` label set to "deployment" or "l1" are tracked, while others are set as inactive in service discovery. `Drop` action can be used as the opposite of `keep`.


# Cloudwatch Exporter

The Cloudwatch exporter facilitates the retrieval of Cloudwatch metrics from AWS and feeds them into Prometheus. Follow these steps to set up and configure the Cloudwatch exporter:

1. **Installation**:
   - Download the Cloudwatch exporter. Check the [official GitHub repository](https://github.com/prometheus/cloudwatch_exporter) for the latest version.
   ```bash
   wget -O cloudwatch_exporter.jar http://search.maven.org/remotecontent?filepath=io/prometheus/cloudwatch/cloudwatch_exporter/0.8.0/cloudwatch_exporter-0.8.0-jar-with-dependencies.jar
   sudo apt-get install -y openjdk-11-jre-headless
   ```

2. **AWS Configuration**:
   - Create or edit the AWS credentials file.
   ```bash
   mkdir -p ~/.aws/
   vim ~/.aws/credentials
   ```
   Add your AWS access key and secret access key:
   ```ini
   [default]
   aws_access_key_id=YOUR_ACCESS_KEY
   aws_secret_access_key=YOUR_SECRET_ACCESS_KEY
   ```

3. **Exporter Configuration**:
   - Create a `cloudwatchexporter.yml` file and define the metrics to retrieve from AWS.
   ```yaml
   region: ap-south-1
   metrics:
     - aws_namespace: AWS/EC2
       aws_metric_name: CPUUtilization 
       aws_dimensions: [InstanceId]
       aws_statistics: [Average]
   ```

4. **Run Cloudwatch Exporter**:
   Execute the Cloudwatch exporter with Java:
   ```bash
   /usr/bin/java -jar cloudwatch_exporter.jar 9106 cloudwatchexporter/cloudwatchexporter.yml
   ```

5. **Prometheus Configuration**:
   Update `prometheus.yml` to include the Cloudwatch exporter job:
   ```yaml
   - job_name: cloudwatch
     static_configs:
     - targets: ['localhost:9106']
   ```

6. **Metrics**:
   View available Cloudwatch metrics [here](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/viewing_metrics_with_cloudwatch.html).

# Mysql Exporter

The MySQL exporter enables the collection of MySQL metrics for Prometheus monitoring. Follow these steps to set up the MySQL exporter:

1. **MySQL Installation**:
   Install MySQL server:
   ```bash
   sudo apt update
   sudo apt install mysql-server
   ```

2. **MySQL User Setup**:
   Create a MySQL user for the exporter:
   ```sql
   CREATE USER 'exporter'@'localhost' IDENTIFIED BY 'Passw0rd' WITH MAX_USER_CONNECTIONS 3;
   GRANT PROCESS, REPLICATION CLIENT, SELECT ON *.* TO 'exporter'@'localhost';
   ```

3. **MySQL Exporter Installation**:
   - Download the MySQL exporter from the [official GitHub repository](https://github.com/prometheus/mysqld_exporter/releases).
   - Create a `.my.cnf` file with MySQL credentials:
   ```ini
   [client]
   user=exporter
   password=Passw0rd
   ```

4. **Run MySQL Exporter**:
   Execute the MySQL exporter:
   ```bash
   ./mysql_exporter --config.my-cnf=./.my.cnf
   ```

5. **Prometheus Configuration**:
   Add the MySQL exporter job to `prometheus.yml`:
   ```yaml
   - job_name: 'mysql_exporter'
     static_configs:
     - targets: ['localhost:9104']
   ```

6. **Queries**:
   Utilize queries like `mysql_version_info` and `mysql_global_status_uptime` on the Prometheus web interface.

# Custom Exporter

Develop and deploy custom exporters according to your specific requirements. Add their addresses to `prometheus.yml` for integration into the Prometheus ecosystem.

# Query with API through HTTP

Access Prometheus query API endpoints through HTTP. Here are some examples:

- Query for the `up` metric:
  ```
  localhost:9090/api/v1/query?query=up
  ```
- Query for the `prometheus_http_request_total` metric over a 1-minute interval:
  ```
  localhost:9090/api/v1/query?query=prometheus_http_request_total[1m]
  ```
- Get a list of targets:
  ```
  localhost:9090/api/v1/targets
  ```
- Retrieve active targets:
  ```
  localhost:9090/api/v1/targets?state=active
  ```

For a comprehensive list of Prometheus API endpoints, refer to the [official documentation](https://prometheus.io/docs/prometheus/latest/querying/api/).