.. _DRY: https://en.wikipedia.org/wiki/Don%27t_repeat_yourself

Overview
========

The entire functionality of :mod:`~dash_building_blocks` drives on the 
:class:`~dash_building_blocks.base.Block` and 
:class:`~dash_building_blocks.base.Store` classes.

Block
^^^^^

The :class:`Block` is the basic "building unit" of object-oriented Dash code.
Inheriting :class:`Block` provides us with some simple but useful tools for
creating a custom "block" class that encapsulates a layout of components
and any relevant callbacks.

Note that the :class:`Block` class itself is an abstract class and cannot be
instantiated.
::

    >>> import dash_building_blocks as dbb
    >>> block = dbb.Block()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      ...
    NotImplementedError

This is because all :class:`Block`-inheriting classes require at minimum a
``layout`` method to be defined. At initialization, whatever is returned by
the defined ``layout`` method will become the permanent ``layout`` attribute
of the instantiated block object. This is a purposefully restricting feature
that ensures that any Dash component ids defined within the block layout
are globally unique. More on that later.

Let's take a look at a minimal block implementation::

    import dash_html_components as html
    import dash_building_blocks as dbb

    class MyBlock(dbb.Block):

        def layout(self):
            return html.Div('hello world')

We can then instantiate it::

    block = MyBlock()

    print(block.layout)

Output::

    Div('hello world')

As you can see, the ``html.Div('hello world')`` we implemented
the ``MyBlock.layout`` method to return became the ``layout`` attribute at
initialization of :class:`Block`. We could potentially assign this simple div as
the layout of a ``Dash`` app object::

    import dash

    app = dash.Dash()
    app.layout = block.layout
    
    if __name__ == '__main__':
        app.run_server()

Ok, but so what? We aren't being very productive here. We just used a few
extra lines of code (to define MyBlock) yet did not accomplish anything extra
... Let's look at a slightly more productive example.

Say we want to create a block of components and callbacks that will be
repeated a few times. In this case let's make a simple ``Parrot`` block
that repeats whatever a ``Human`` says.

First, let's try this idea with pure Dash::

    import dash
    from dash.dependencies import Input, Output, State
    import dash_html_components as html
    import dash_core_components as dcc

    app = dash.Dash()

    human_div = html.Div('Hello World', id='human-says')

    parrot_div = html.Div(id='parrot-says')

    app.layout = html.Div(
        [human_div, parrot_div]
    )

    @app.callback(
        Output('parrot-says', 'children'),
        [Input('human-says', 'children')]
    )
    def update_what_parrot_says(whatever_human_says):
        return whatever_human_says

    ...

This is easy enough. But there is only one parrot. What if we want more 
parrots? In order to keep the code DRY_, we can do something along these
lines::

    app = dash.Dash()

    human_div = html.Div('Hello World', id='human-says')

    def create_parrot(name):
        # create div
        parrot_id = 'parrot-{}-says'.format(name)
        parrot_div = html.Div(id=parrot_id)

        # create dependencies
        dependencies = {
            'output': Output(parrot_id, 'children'),
            'inputs': [Input('human-says', 'children')]
        }

        # define callback function
        def callback_f(whatever_human_says):
            return '{} says: {}'.format(name, whatever_human_says)

        return {
            'div': parrot_div,
            'dependencies': dependencies,
            'callback': callback_f
        }

    parrot_names = ['iago', 'zazu', 'skully']

    parrots = [create_parrot(name) for name in parrot_names]

    app.layout = html.Div(
        [human_div] + [parrot['div'] for parrot in parrots]
    )

    for parrot in parrots:
        app.callback(**parrot['dependencies'])(parrot['callback'])

This is not too bad but our code is starting to be less readable and we need 
to use string formatting to ensure that Dash component ids are all globally
unique; as a project becomes large and complex this can be a daunting task.

Let's run with this idea but instead leverage ``dash_building_blocks``. 
There will only be one ``Human`` block, so we don't need to worry about its
reusability. Still we can use the ``dbb.Block`` to encapsulate the ``Human``-\
coupled components, for organization and readibility sakes; as well as the
possibility that we will extend its functionality in the future with, say, 
``Human``-coupled callbacks.

Let's define our ``Human`` block class.
::

    class Human(dbb.Block):
        
        def layout(self):
            return html.Div('Hello World', id=self.register('says'))

Note the use of ``self.register('says')``. Inherited from :class:`Block`,
this function allows us to define a localized id, which is created, stored
internally, and returned by the function for convenience. Behind the scenes,
every :class:`Block` subclass object maintains a mapping of localized id to its
globally unique counterpart. This means don't have to worry about global ids
getting mixed up (unless we explicitly mess them up). More on that later, but
for now, just know that ``self.register('says')`` will return an id like 
"*human-<id>-says*", where *id* is a random alphanumerical string by
default unless explicitly specified during block initialization.

Now let's define our ``Parrot`` block class.
::

    class Parrot(dbb.Block):
        
        def layout(self):
            return html.Div(id=self.register('says'))
        
        def callbacks(self, human):
            @self.app.callback(
                self.output('says', 'children'),
                [human.input('says', 'children')]
            )
            def update_what_i_say(whatever_human_says):
                return '{} says: {}'.format(self.data.name, 
                                            whatever_human_says)

Because all parrots should have the ability to repeat what some human says,
we defined a ``callbacks`` method that expects as input a ``Human`` block
and creates the appropriate callback. You may have noticed that ``self.app``
and ``self.data`` were used and wondered where they came from. These will be
available as we will pass them as arguments when initializing the block. 

You may also have noticed the ``self.output`` and ``human.input`` calls. 
These convenience methods are inherited from :class:`Block` and return the
Dash dependency respective to the localized component id and property
provided. To illustrate, let's quickly use the ``MyBlock`` we 
implemented earlier::

    >>> block = MyBlock()
    >>> block.layout
    Div('Hello World')
    >>> block.id
    'my-block-ze7V9nTWCJ6thubV'
    >>> block.register('helloworld')
    'my-block-ze7V9nTWCJ6thubV-helloworld'
    >>> dep = block.input('helloworld', 'children')
    >>> dep
    <dash.dependencies.Input at 0x11dec14e0>
    >>> dep.component_id
    'my-block-ze7V9nTWCJ6thubV-helloworld'
    >>> dep.component_property
    'children'
    >>> block.output('helloworld', 'children')
    <dash.dependencies.Output at 0x11dec1518>
    >>> block.state('helloworld', 'children')
    <dash.dependencies.State at 0x11dec12e8>

See the :doc:`API documentation <api>` for more detail.

With our ``Human`` and ``Parrot`` block classes defined, we can put them in 
action. We must make sure that we pass in ``data={'name': name}`` when 
initializing our ``Parrot``\ s so that ``self.data.name`` is available as 
expected in our definition of the parrot ``update_what_i_say`` callback.

Let's create the app:
::

    app = dash.Dash()

    human = Human()
            
    parrot_names = ['iago', 'zazu', 'skully']

    parrots = [Parrot(app=app, data={'name': name}) 
               for name in parrot_names]

    app.layout = html.Div(
        [ human.layout ] + [ parrot.layout for parrot in parrots ]
    )

    for parrot in parrots:
        parrot.callbacks(human)

The high-level definition of the app is now decoupled from the block-level
definitions, improving readibility. 

Store
^^^^^

.. warning:: TODO