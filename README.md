[![Build Status](https://circleci.com/gh/cloudify-examples/salt-blueprint.svg?style=shield&circle-token=:circle-token)](https://circleci.com/gh/cloudify-examples/salt-blueprint)

##  Salt Blueprint

This blueprint creates a Salt Master and Salt Minion on Centos 7 VMs in a Cloudify Management Environment.


## prerequisites

You will need a *Cloudify Manager* running in either AWS, Azure, or Openstack.

If you have not already, set up the [example Cloudify environment](https://github.com/cloudify-examples/cloudify-environment-setup). Installing that blueprint and following all of the configuration instructions will ensure you have all of the prerequisites, including keys, plugins, and secrets.


### Step 1: Install the demo application

In this step, you will first gather two pieces of information from your Cloud account: the parameters of a Centos 7.0 image and a medium sized image. This info is already provided for AWS us-east-1 and Azure us-east.

Next you provide those inputs to the blueprint and execute install:

#### For AWS run:

```shell
$ cfy install \
    https://github.com/cloudify-examples/simple-kubernetes-blueprint/archive/4.0.1.zip \
    -b demo \
    -n aws-blueprint.yaml
```


#### For Azure run:

```shell
$ cfy install \
    https://github.com/cloudify-examples/simple-kubernetes-blueprint/archive/4.0.1.zip \
    -b demo \
    -n azure-blueprint.yaml
```


#### For Openstack run:

```shell
$ cfy install \
    https://github.com/cloudify-examples/simple-kubernetes-blueprint/archive/4.0.1.zip \
    -b demo \
    -n openstack-blueprint.yaml -i flavor=[MEDIUM_SIZED_FLAVOR] -i image=[CENTOS_7_IMAGE_ID]
```


The `install` command output should look similar to this, followed by a ton of logs:

```shell
Executing workflow install on deployment salt09 [timeout=900 seconds]
Deployment environment creation is in progress...
2017-06-20 15:31:42.032  CFY <salt09> Starting 'install' workflow execution
```


You may notice that the installation gets stuck in a phase like this for some time:

```shell
2017-06-20 15:36:10.643  CFY <demo> [salt_minion_8the4s.configure] Sending task 'script_runner.tasks.run' [retry 2/60]
2017-06-20 15:36:10.659  CFY <demo> [salt_minion_8the4s.configure] Task started 'script_runner.tasks.run' [retry 2/60]
2017-06-20 15:36:13.749  LOG <demo> [salt_minion_8the4s.configure] INFO: Downloaded scripts/salt/configure_minion.py to /tmp/FRN2Q/configure_minion.py
2017-06-20 15:36:13.969  CFY <demo> [salt_minion_8the4s.configure] Task failed 'script_runner.tasks.run' -> Salt is not yet running. [retry 2/60]
Timed out waiting for workflow 'install' of deployment 'demo' to end. The execution may still be running properly; however, the command-line utility was instructed to wait up to 900 seconds for its completion.
* Run 'cfy executions list' to determine the execution's status.
* Run 'cfy executions cancel c0a4bd51-ba7b-4f7f-8bb4-89bb6d76e97a' to cancel the running workflow.
* Run 'cfy events list --tail --include-logs --execution-id c0a4bd51-ba7b-4f7f-8bb4-89bb6d76e97a' to retrieve the execution's events/logs
```


This is because the configure script is waiting for a salt service to begin running. Generally, the workflow will succeed even if the CLI times out at this point. However, there is also a chance that an issue with the cloud-init service at your IaaS failed to send the installation instructions properly.


### Verify everything

When you see this output, you can check to see that the Salt Minion is connected to the Salt Master:

```shell
2017-06-20 15:37:05.932  CFY <salt09> 'install' workflow execution succeeded
Finished executing workflow install on deployment demo
```

#### First get the node-instance IDS:

```shell
$ cfy node-instances list -d demo
+----------------------------+---------------+--------------------+---------------------+---------+------------+----------------+------------+
|             id             | deployment_id |      host_id       |       node_id       |  state  | permission |  tenant_name   | created_by |
+----------------------------+---------------+--------------------+---------------------+---------+------------+----------------+------------+
...
|      public_ip_3flkd6      |     salt09    |                    |      *public_ip*    | started |  creator   | default_tenant |   admin    |
...
```


#### Look for the _id_ for _node_id_ public ip, and find out the value:

```shell
$ cfy node-instances get public_ip_3flkd6
```

```shell
Retrieving node instance public_ip_3flkd6

Node-instance:
...

Instance runtime properties:
...
	aws_resource_id: **.**.**.161
...
```


#### Then SSH into the master and check to see that the Minions are added:

```shell
$ ssh -i ~/.ssh/cfy-agent-key-aws ec2-user@**.**.**.161
$ sudo salt-key -L
Accepted Keys:
ip-10-10-1-145
ip-10-10-1-80
Denied Keys:
Unaccepted Keys:
Rejected Keys:
```

#### You can now uninstall:

```shell
$ cfy uninstall --allow-custom-parameters demo
```
