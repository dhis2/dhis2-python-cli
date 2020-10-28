import os

import click
from pkg_resources import iter_entry_points

from .inventory import Inventory, parse_file, parse_obj, resolve
from .inspect import inspect
defaultInventory = {"hosts": {}, "groups": {}}


class CliContext(object):
    def __init__(self, inventory=None, debug=False):
        if inventory:
            self.inventory: Inventory = parse_file(os.path.abspath(inventory))
        else:
            self.inventory: Inventory = parse_obj(defaultInventory)

        self.debug = debug


@click.group()
@click.version_option()
@click.option("-i", "--inventory")
@click.option("-d", "--debug", is_flag=True)
@click.pass_context
def cli(ctx, inventory, debug):
    ctx.obj = CliContext(inventory, debug)


@cli.command("inspect")
@click.argument("id")
@click.pass_obj
def cmd_inspect(ctx, id):
    hosts = resolve(id, ctx.inventory)
    inspect(hosts)


@cli.group("inventory")
def cli_inventory():
    pass


@cli_inventory.command("schema")
def cmd_inventory_schema():
    click.echo(Inventory.schema_json(indent=2))


@cli_inventory.command("resolve-id")
@click.argument("id")
@click.pass_obj
def cmd_inventory_resolve(ctx, id):
    hosts = resolve(id, ctx.inventory)

    for host in hosts:
        print(host.json())


# register additional plugins
for entry_point in iter_entry_points(group="dhis2.plugin", name=None):
    entry_point.load()(cli)  # check for valid function
