#!/bin/bash

# issue this command after setting up the associated maas cli profile
POD_EP=`maas humble pods read | jq .[0].resource_uri`; POD_ID=`basename "${POD_EP%\"}"`; maas humble pod delete $POD_ID

# issue this command locally on the VM host
virsh list --all | grep mpg  | awk {'print $2'} | xargs -I % virsh destroy % ; virsh list --all | grep mpg  | awk {'print $2'} | xargs -I % virsh undefine % ; virsh pool-destroy mpg-volume-pool; virsh pool-undefine mpg-volume-pool; rm -f ~/mpg-pool/*
