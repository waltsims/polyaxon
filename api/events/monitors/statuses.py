# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import logging

from kubernetes import watch

from libs.redis_db import RedisJobContainers
from events.tasks import handle_events_job_statues
from spawner.utils.jobs import get_job_state

logger = logging.getLogger('polyaxon.monitors.statuses')


def update_job_containers(event, job_container_name):
    if event.status.container_statuses is None:
        return

    def get_container_id(container_id):
        if not container_id:
            return None
        if container_id.startswith('docker://'):
            return container_id[len('docker://'):]
        return container_id

    for container_status in event.status.container_statuses:
        if container_status.name != job_container_name:
            continue

        container_id = get_container_id(container_status.container_id)
        if container_id:
            job_uuid = event.metadata.labels['job_id']
            if container_status.state.running is not None:
                logger.info('Monitoring (container_id, job_uuid): ({}, {})'.format(container_id,
                                                                                   job_uuid))
                RedisJobContainers.monitor(container_id=container_id, job_uuid=job_uuid)


def run(k8s_manager, experiment_type_label, job_container_name, label_selector=None):
    w = watch.Watch()

    for event in w.stream(k8s_manager.k8s_api.list_namespaced_pod,
                          namespace=k8s_manager.namespace,
                          label_selector=label_selector):
        logger.info("Received event: %s" % event)
        job_state = get_job_state(event, job_container_name, experiment_type_label)

        if job_state:
            logger.info("Updating job container: {}".format(event['object']))
            update_job_containers(event['object'], job_container_name)
            logger.info("Publishing event: {}".format(job_state))
            handle_events_job_statues.delay(payload=job_state)
