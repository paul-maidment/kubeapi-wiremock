#
# Dump Stub Objects from an actual KubeAPI instance so that we can use these stubs for mocks.
#

from subprocess import PIPE, run
import jq
import json
import uuid
import os

class StubGenerator:

    def generateGetStatus200(self, name, url, response_body):
        return self.generate(
            str(uuid.uuid4()),
            name,
            url,
            "GET",
            200,
            response_body
        )

    def generate(self, uuid, name, url, method, status, response_body):
        return self.template\
            .replace("###UUID###", uuid)\
            .replace("###NAME###", name)\
            .replace("###URL###", url)\
            .replace("###METHOD###", method)\
            .replace("###STATUS###", str(status))\
            .replace("###RESPONSE_BODY###", response_body)

    template = """
    {
        "mappings" : [ {
            "id" : "###UUID###",
            "name" : "###NAME###",
            "request" : {
            "urlPath" : "###URL###",
            "method" : "###METHOD###"
            },
            "response" : {
            "status" : ###STATUS###,
            "body" : ###RESPONSE_BODY###,
            "headers" : { }
            },
            "uuid" : "###UUID###",
            "persistent" : true,
            "priority" : 5,
            "postServeActions" : [ ]
        }],
        "meta" : {
            "total" : 1
        }
    }"""


def getKubeAPIAddress():
    command = ["kubectl", "config" ,"view" , "-o", "jsonpath={.clusters[0].cluster.server}"]
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    if result.returncode != 0:
        raise Exception("Could not get the address of KUBE_API due to an unexpected error!")
    if "http" not in result.stdout:
        raise Exception("Got an unexpected value for the address of KubeAPI server, are you sure that your kubeconfig is properly configured?")
    return result.stdout

def getBodyForGetRequest(address:str):
    curlCommand = ["curl", address, "--cacert", "/root/.minikube/ca.crt", "--cert", "/root/.minikube/profiles/minikube/client.crt", "--key", "/root/.minikube/profiles/minikube/client.key"]
    result = run(curlCommand, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    if result.returncode != 0:
        raise Exception("Could not perform fetch against address : " + address + " error = " + result.stderr)
    return result.stdout

def getResponse(kubeApiAddress:str, uri:str, jqParam:str):
    body = getBodyForGetRequest(kubeAPIAddress + uri)
    body = jq.compile(jqParam).input(json.loads(body)).text()
    body = json.dumps(body)
    stubGenerator = StubGenerator()
    response = stubGenerator.generateGetStatus200(uri, uri, body)
    return response

kubeAPIAddress = getKubeAPIAddress()

endpoints = [
    "/api/v1",
    "/apis/apps/v1",
    "/apis/apps/v1/namespaces/kube-system/deployments",
    "/api/v1/namespaces/kube-system/pods"
]

for endpoint in endpoints:
    response = getResponse(kubeAPIAddress, endpoint, '.')
    f = open(os.getcwd() + "/src/stubs/mappings/" + endpoint.replace("/", "_")+".json", "w")
    f.write(response)
    f.close()
