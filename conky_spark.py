#!/usr/bin/env python3
# coding: utf-8

import json
import argparse
from urllib import request

start_port = 4040


class Node:
    def __init__(self, ip=None, name=None):
        self.ip = ip
        self.name = name
        self.http_addr = 'http://' + a.ip
        self.spark_contexts = []
        self.request_spark_contexts()

    def get_stat(self):
        if len(self.spark_contexts) == 0:
            return self.name + ': no apps'
        sc_stats = str()
        for sc in self.spark_contexts:
            sc_stats += sc.get_stat() + '\n'
        return 'node: ' + self.name + '\n' + sc_stats[:-1]

    def request_spark_contexts(self):
        keep_looking = True
        try_port = start_port
        while keep_looking:
            new_url = self.http_addr + ':' + str(try_port) + '/api/v1/applications'
            text = None
            try:
                with request.urlopen(new_url) as f:
                    text = f.read()
                    sc = json.loads(text.decode('utf-8'))
                    apps = []
                    for app in sc:
                        apps.append(App(self.ip, try_port, app['id'], app['name']))
                    self.spark_contexts.append(SparkContext(self.ip, try_port, apps))
            except Exception:
                keep_looking = False
                continue
            try_port += 1


class SparkContext:
    def __init__(self, ip=None, port=None, apps=None):
        self.ip = ip
        self.port = port
        self.apps = apps

    def get_stat(self):
        apps_stat = str()
        for app in self.apps:
            apps_stat += app.get_stat() + '\n'
        return apps_stat[:-1]


class App:
    def __init__(self, ip=None, port=None, id=None, name=None):
        self.ip = ip
        self.port = port
        self.id = id
        self.name = name
        self.jobs = []
        self.request_stages()

    def request_jobs(self):
        http_addr = 'http://' + self.ip + ':' + str(self.port) + '/api/v1/applications/' + self.id + '/jobs'
        try:
            with request.urlopen(http_addr) as f:
                text = f.read()
                jobs_text = json.loads(text.decode('utf-8'))
                for job in jobs_text:
                    self.jobs.append(Job(job['jobId'], job['name'], job['numTasks'], job['numCompletedTasks']))
        except Exception:
            pass

    def request_stages(self):
        http_addr = 'http://' + self.ip + ':' + str(self.port) + '/api/v1/applications/' + self.id + '/stages'
        try:
            with request.urlopen(http_addr) as f:
                text = f.read()
                jobs_text = json.loads(text.decode('utf-8'))
                for job in jobs_text:
                    self.jobs.append(Job(job['stageId'], job['name'], (job['numCompleteTasks'] + job['numActiveTasks']  + job['numFailedTasks']), job['numCompleteTasks']))
        except Exception:
            pass

    def get_stat(self):
        jobs_stats = str()
        for job in self.jobs:
            jobs_stats += job.get_stat() + '\n'
        return '  ' + 'app: ' + self.name + ':\n' + jobs_stats[:-1]


class Job:
    def __init__(self, id=None, name=None, num_tasks=None, num_completed_tasks=None):
        self.id = id
        self.name = name
        self.num_tasks = num_tasks
        self.num_completed_tasks = num_completed_tasks

    def get_stat(self):
        p = int((self.num_completed_tasks/self.num_tasks) * 100) if self.num_tasks > 0 else 0
        f = self.name.find('/')
        l = self.name.rfind('/')
        name = self.name if f == l else self.name[:f] + self.name[l + 1:]
        bar = '    ' + '${execbar echo ' + str(p) + '}'
        text = '    ' + str(p) + '% : '
        text += str(self.num_completed_tasks) + '/' + str(self.num_tasks) + ' : ' + str(self.id) + '\n' + '    ' + name
        return bar + '\n' + text


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip')
    parser.add_argument('--name')
    a = parser.parse_args()
    n = Node(a.ip, a.name)
    print(n.get_stat())
