# ansible-inventory

This package was built to make it easier to configure Ansible dynamic
inventories to create the groups that you want based on your own
logic.

So if you have a naming scheme that implies groups, then you should be
able to just define that in your inventory script and have the groups
create themselves.

Take for example a host with the name: `SEDBPG01`

In this particular scheme this host tells us:

* `SE` - Sweden
* `DB` - Database
* `PG` - PostgreSQL
* `01` - It's the first database server

And I want to be able to create a dynamic inventory with the following
groups: `sweden`, `database`, `postgres`.

