Motivation
==========
When first becoming acquainted with the wonderful
`Dash <https://plot.ly/products/dash/>`_ framework, it is not immediately
obvious how to write and organize code that is scalable, modular, and
`DRY <https://en.wikipedia.org/wiki/Don%27t_repeat_yourself>`_ for
increasingly complex apps.

Although, `Dash <https://plot.ly/products/dash/>`_ documentation does touch on
application structure
`here <https://dash.plot.ly/dash-deployment-server/application-structure>`_,
some felt that something was still missing that could be resolved with a more
object-oriented approach. See
`this issue on GitHub <https://github.com/plotly/dash/issues/61>`_ for a very
good discussion on this topic. The foundation for ``dash_building_blocks``
was bourne out of this discussion, particularly `Ned's comment
<https://github.com/plotly/dash/issues/61#issuecomment-316925655>`_
introducing the idea of a ``BaseBlock`` that would link a layout to its
relevant callbacks, effectively creating a reusable and inheritable "block" of
Dash components.