CloudBirds
----------

CloudBirds is an autoscaling framework to elastically manage platforms and applications within cloud environments. It uses a decentralized flocking artificial intelligence to do this.

While the cloudbirds framework is not tightly coupled to the use of virtual machines or any particular infrastructure-as-a-service layer, drivers are currently available only for VMs running on openstack.

There are significant performance advantages to using Piston Enterprise OpenStack, due to speed and memory advantages of VMS-based instance cloning.

RPC Options:

 * Gossip protocol over webhooks, with webhooks endpoints announced via SNMP
 * PubSubHubBub against servicekey (unique to flock)
 * Gossip protocol over webhooks, with ZeroConf-based bird discovery
 * Other? (RabbitMQ, etc.)

Current load of the VM is monitored using SNMP data, polled locally by the CloudBirds agent.
All VMs in a "Flock" (which corresponds to a single tier in an n-tiered application) are related to each other in a parent-child hierarchy.
Each CloudBird uses a finite-state-machine internally to manage workflow.
Child and Parent CloudBirds respond to changes in state of their relatives.
Overall flock status (including current state of each CloudBird) is passed through the flock using a gossip protocol implemented over webhooks.

TESTING and TUNING:

The ideal mechanism to tune a CloudBird flock is via genetic-algorithm-based adjustment of the primary tuning parameters.
This can be achieved using Grinder to run tests against the hurt-me testing web application, optimizing for an index that factors in total flock throughput, cost per request (based on number of running instances).

Tuning parameters:

 * load-to-respawn
 * delay-before-respawn
 * back-off (Overwhelmed to bored)
 * Number of eggs per parent bird
 * TTL hops for gossip protocol (aka world visibility per bird)


TODO: Everything.

 - Make the webhooks also deliver config data?
 - Read config data from json or yaml
 - Immortals are ranked by age - young immortals can be terminated if they're excessive.

References
==========

 * http://progrium.com/blog/2012/11/26/x-callback-header-an-evented-web-building-block/
 * http://progrium.com/blog/2012/11/19/from-webhooks-to-the-evented-web/
 * http://john-sheehan.com/post/36704862225/x-callback-header-evented-web-building-block-by
 * https://code.google.com/p/pubsubhubbub/
 * http://www.slideshare.net/brevoortm/the-evented-web
 * http://highscalability.com/blog/2011/11/14/using-gossip-protocols-for-failure-detection-monitoring-mess.html
 * http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.160.2604
 * http://pysnmp.sourceforge.net/examples/current/index.html

