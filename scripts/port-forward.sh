#!/bin/bash

# Start port forwarding
start() {
  echo "Starting port forwarding..."
  nohup kubectl port-forward svc/task-service 8000:8000 > /dev/null 2>&1 &
  echo $! > /tmp/task-service-pf.pid
  nohup kubectl port-forward svc/prometheus 9090:9090 > /dev/null 2>&1 &
  echo $! > /tmp/prometheus-pf.pid
  nohup kubectl port-forward svc/grafana 3000:3000 > /dev/null 2>&1 &
  echo $! > /tmp/grafana-pf.pid
  echo "Port forwarding started"
}

# Stop port forwarding
stop() {
  echo "Stopping port forwarding..."
  [ -f /tmp/task-service-pf.pid ] && kill $(cat /tmp/task-service-pf.pid) 2>/dev/null
  [ -f /tmp/prometheus-pf.pid ] && kill $(cat /tmp/prometheus-pf.pid) 2>/dev/null
  [ -f /tmp/grafana-pf.pid ] && kill $(cat /tmp/grafana-pf.pid) 2>/dev/null
  echo "Port forwarding stopped"
}

# Show status
status() {
  echo "Port forwarding status:"
  pgrep -f "kubectl port-forward svc/task-service" > /dev/null && echo "task-service: running" || echo "task-service: stopped"
  pgrep -f "kubectl port-forward svc/prometheus" > /dev/null && echo "prometheus: running" || echo "prometheus: stopped"
  pgrep -f "kubectl port-forward svc/grafana" > /dev/null && echo "grafana: running" || echo "grafana: stopped"
}

case "$1" in
  start)  start ;;
  stop)   stop ;;
  status) status ;;
  restart) stop; start ;;
  *) echo "Usage: $0 {start|stop|status|restart}" ;;
esac
