.. _DRY: https://en.wikipedia.org/wiki/Don%27t_repeat_yourself

Overview
========

The entire functionality of :mod:`~dash_building_blocks` drives on the 
:class:`~dash_building_blocks.base.Block` and 
:class:`~dash_building_blocks.base.Store` classes.

Block
^^^^^

The :class:`~dash_building_blocks.base.Block` is the basic "building unit" 
of object-oriented Dash code.
Inheriting :class:`~dash_building_blocks.base.Block` provides us with some
simple but useful tools for
creating a custom "block" class that encapsulates a layout of components
and any relevant callbacks.

Note that the :class:`~dash_building_blocks.base.Block` class itself is an abstract class and cannot be
instantiated.
::

    >>> import dash_building_blocks as dbb
    >>> block = dbb.Block()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      ...
    NotImplementedError

This is because all :class:`~dash_building_blocks.base.Block`\ -inheriting
classes require at minimum a
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
initialization of :class:`~dash_building_blocks.base.Block`. We could
potentially assign this simple div as
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

    if __name__ == '__main__':
        app.run_server()

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

Note the use of ``self.register('says')``. Inherited from 
:class:`~dash_building_blocks.base.Block`,
this function allows us to define a localized id, which is created, stored
internally, and returned by the function for convenience. Behind the scenes,
every :class:`~dash_building_blocks.base.Block` subclass object maintains 
a mapping of localized id to its
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
These convenience methods are inherited from 
:class:`~dash_building_blocks.base.Block` and return the
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

And run it:
::

    if __name__ == '__main__':
        app.run_server()

The high-level definition of the app is now decoupled from the block-level
definitions, improving readibility. 

Store
^^^^^

Let's extend our simple human & parrot app to be a little more dynamic.
Instead of the human saying a static phrase that all parrots repeat, let's
say that we want the human to select a parrot and command it (and not the
others) to repeat his current phrase. A good approach here may be to
package the selected parrot name and current human phrase into a hidden div
that acts as intermediate data storage. Sharing data between callbacks using
hidden divs is very common and `suggested in the Dash user guide
<https://dash.plot.ly/sharing-data-between-callbacks>`_.

To streamline the creation and use of these hidden storage divs, 
:mod:`dash_building_blocks` provides the :class:`~dash_building_blocks
.base.Store` class. Its interface 
is similar to that of :class:`~dash_building_blocks.base.Block`\ s but 
slightly
different due to its more specific function. It is hidden by default but may
be made visible by specifying the ``hidden=False`` option at initialization,
which can come in handy when debugging.

Before we get to using the :class:`~dash_building_blocks.base.Store`, let's
refactor what we already have as necessary.

First, the ``Human``. Instead of holding a static phrase, we want the human
to select between available parrots and have an editable phrase; a
dropdown, text-input, and submit button will do the trick.
::

    class Human(dbb.Block):
        
        def layout(self):
            return html.Div([
                dcc.Dropdown(
                    options=self.data.options,
                    id=self.register('select')
                ),
                dcc.Input(id=self.register('says')),
                html.Button('Speak!', id=self.register('command-button'))
            ])

Next, the ``Parrot``. Let's put the object-orientation to work and create
a ``self.template`` attribute to hold the template for the parrot's message;
that way we can set it in ``layout`` during initialization and have it
available when updating in the callback as well (keeping things DRY_). Since
we are planning on getting our callback dependency data from some hidden
storage div, we change the ``Parrot.callbacks()`` parameter to some
``intermediate_input`` that we will expect to be of type ``dash.dependencies.
.Input``.
::

    # we use these in the callback, make sure we import them
    from dash.exceptions import PreventUpdate
    import json
    
    class Parrot(dbb.Block):
        
        def layout(self):
            self.template = self.data.name + ' says: {}'
            says = self.template.format('squawk!')
            return html.Div(says, id=self.register('says'))
        
        def callbacks(self, intermediate_input):
            @self.app.callback(
                self.output('says', 'children'),
                [intermediate_input]
            )
            def update_what_i_say(intermediate_data):
                intermediate_data = json.loads(intermediate_data)
                if intermediate_data['name'] == self.data.name:
                    return self.template.format(intermediate_data['say'])
                else:
                    raise PreventUpdate

Note that this means Parrot could easily integrate with raw :mod:`dash` code
now as it no longer relies on another block as previously. For example:
::

    ...
    parrot.callback(Input('intermediate_div', 'children'))
    ...

This is the kind
of design choice that is completely up to the user; the goal of 
:mod:`~dash_building_blocks` has always been for it to work with :mod:`dash`
without pigeonholing the user into a specific design framework. In fact, 
throughout this user guide we
will use ``callbacks`` as the standard name for the function where we define
a block's callbacks, but this is nowhere set in stone. Besides the required
``layout`` method, how you define the block class is completely up to you.

Back to our refactoring.
Using the store object and the modifications to our little parrots example,
we can achieve the extra dynamic functionality while keeping our code
organized and clean.
::

    app = dash.Dash()

    store = dbb.Store(app)

    store.register('human-command')

    parrot_names = ['iago', 'zazu', 'skully']

    options = [{'label': name, 'value': name} 
               for name in parrot_names]

    human = Human(data={'options': options})

    parrots = [Parrot(app=app, data={'name': name}) 
               for name in parrot_names]

    app.layout = html.Div(
        [
            human.layout
        ] + [
            parrot.layout for parrot in parrots
        ] + [
            store.layout
        ]
    )

    @app.callback(
        store.output('human-command'),
        inputs=[human.input('command-button', 'n_clicks')],
        state=[human.state('select', 'value'), 
               human.state('says', 'value')]
    )
    def command_parrot(n_clicks, selected_parrot, what_to_say):
        return json.dumps({'name': selected_parrot,
                           'say': what_to_say})

    for parrot in parrots:
        parrot.callbacks(store.input('human-command'))

    app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})

    if __name__ == '__main__':
        app.run_server()

Important to note is the use of ``store``. We first registered
``'human-command'`` so the ``store`` knew to create the respective hidden
storage div. We then assigned a callback to update ``human-command``
without specifying the `'children'` property in
``store.output('human-command')`` because unlike blocks, the store
depedencies always contain the ``'children'`` implictly.

.. note::
   :class:`~dash_building_blocks.base.Block` depedencies do default
   the *component_property* to ``'children'`` if not provided, though the
   pythonic way is to be explicit.


