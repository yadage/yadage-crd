from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import json
import os
import logging

log = logging.getLogger(__name__)

logging.basicConfig(level = logging.INFO)

def make_desired(name, spec):
   configname =  "{}-yadage-config".format(name)
   claimname  = os.environ['YADKUBE_CLAIM']
   backend = {
      'backend': 'kubedirectjob',
      'backendopts': {
         'kubeconfig': 'incluster',
         'secrets': {
            'hepauth': os.environ['YADKUBE_AUTH_SECRET'],
            'hepimgcred': [{"name": os.environ['YADKUBE_REGCRED_SECRET']}]
         },
         'resource_prefix': '{}-sub'.format(name),
         'resource_labels': {'component': 'yadage', 'workflow': name}
      }
   }
   spec.update(**backend)
   children = [
       {
         "apiVersion": "v1",
         "data": {
            "workflow.yml": json.dumps(spec, sort_keys = True)
         },
         "kind": "ConfigMap",
         "metadata": {
            "name": configname
         }
      }
      ,
      {
         "apiVersion": "batch/v1",
         "kind": "Job",
         "metadata": {
            "name": "{}-yadage".format(name)
         },
         "spec": {
            "backoffLimit": 0,
            "template": {
               "spec": {
                  "containers": [
                     {
                        "command": [
                           "yadage-run","-f","/etc/config/workflow.yml"
                        ],
                        "image": os.environ['YADKUBE_IMAGE'],
                        "imagePullPolicy":  os.environ['YADKUBE_IMAGE_POLICY'],
                        "name": "runner",
                        "env": [
                           {
                              "name": "YADAGE_SCHEMA_LOAD_TOKEN",
                              "value": os.environ['YADKUBE_PRIVATE_TOKEN'] or "dummy" #metacontroller cannot handling empty strings
                           },
                           {
                              "name": "YADAGE_INIT_TOKEN",
                              "value": os.environ['YADKUBE_PRIVATE_TOKEN'] or "dummy" #metacontroller cannot handling empty strings
                           }
                        ],
                        "volumeMounts": [
                           {
                              "mountPath": "/data",
                              "name": "data"
                           },
                           {
                              "mountPath": "/etc/config",
                              "name": "config-volume"
                           }
                        ],
                        "workingDir": "/data"
                     }
                  ],
                  "restartPolicy": "Never",
                  "volumes": [
                     {
                        "name": "data",
                        "persistentVolumeClaim": {
                           "claimName": claimname
                        }
                     },
                     {
                        "configMap": {
                           "name": configname
                        },
                        "name": "config-volume"
                     }
                  ]
               }
            }
         }
      }   
   ]
   return children

class Controller(BaseHTTPRequestHandler):
   def sync(self, parent, children):
      # Compute status based on observed state.

      job_status = [{k:v for k,v in v['status'].items() if k in ['failed','succeeded','active']} for x,v in children["Job.batch/v1"].items()]

      observed_status = {
         "cmap": len(children["ConfigMap.v1"]),
         "jobs": len(children["Job.batch/v1"]),
         "workflow": job_status[0]if len(job_status) else "not scheduled"
      }

      log.info('CRD sync called for parent {}'.format(parent['metadata']['name']))
      log.info('Observed Status: {}'.format(observed_status))
      # Generate the desired child object(s).
      spec  = parent.get("spec", {})
      name = parent["metadata"]["name"]
    
      desired_children= make_desired(name, spec)
      # desired_children = desired_children[:1]

      log.info('Desired Children: {}'.format([x['metadata'] for x in desired_children]))


      # import time
      # time.sleep(5)
      # print(json.dumps(children, indent = 4))
      log.info('CRD sync done for parent {}'.format(parent['metadata']['name']))

      return {"status": observed_status, "children": desired_children}

   def do_POST(self):
      # Serve the sync() function as a JSON webhook.
      observed = json.loads(self.rfile.read(int(self.headers.getheader("content-length"))))
      desired = self.sync(observed["parent"], observed["children"])

      self.send_response(200)
      self.send_header("Content-type", "application/json")
      self.end_headers()
      self.wfile.write(json.dumps(desired, sort_keys = True))

HTTPServer(("", 80), Controller).serve_forever()
