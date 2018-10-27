API documentation
=================
.. automodule:: dash_building_blocks

Base
^^^^
.. automodule:: dash_building_blocks.base

Block
-------
.. autoclass:: dash_building_blocks.base.Block

    .. autoattribute:: dash_building_blocks.base.Block.id

    .. automethod:: dash_building_blocks.base.Block.layout

    .. automethod:: dash_building_blocks.base.Block.register

    .. automethod:: dash_building_blocks.base.Block.parameters

    .. automethod:: dash_building_blocks.base.Block.callback

    .. automethod:: dash_building_blocks.base.Block.class_id

    .. automethod:: dash_building_blocks.base.Block.input

    .. automethod:: dash_building_blocks.base.Block.output

    .. automethod:: dash_building_blocks.base.Block.state

Store
-----
.. autoclass:: dash_building_blocks.base.Store

    .. autoattribute:: dash_building_blocks.base.Store.layout

    .. automethod:: dash_building_blocks.base.Store.register

    .. automethod:: dash_building_blocks.base.Store.input

    .. automethod:: dash_building_blocks.base.Store.output

    .. automethod:: dash_building_blocks.base.Store.state

Data
----
.. autoclass:: dash_building_blocks.base.Data

    .. automethod:: dash_building_blocks.base.Data.from_dict

    .. automethod:: dash_building_blocks.base.Data.to_dict

Util
^^^^
.. automodule dash_building_blocks.util
   
.. automethod:: dash_building_blocks.util.generate_random_string
   
.. automethod:: dash_building_blocks.util.camelify(name, delims=['-', '_'])
   
.. automethod:: dash_building_blocks.util.decamelify