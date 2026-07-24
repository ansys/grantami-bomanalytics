.. _ref_grantami_bomanalytics_bom_builders:

BoM reference builders
======================

Record reference builder
------------------------

Many types of entity are referenced within a Granta MI database. These references can use several different ways of
identifying the target object. The RecordReferenceBuilder helps to ensure that a reference contains the required
information and to reduce the risk of ambiguous references being provided.

.. autoclass:: ansys.grantami.bomanalytics.bom_types.RecordReferenceBuilder
   :inherited-members:
   :member-order: by_mro_by_source



Attribute reference builder
---------------------------

Records can be referred to by a unique text value, this must be accompanied by a reference to the attribute containing
the value. The AttributeReferenceBuilder helps to ensure that this reference contains the required information and to
reduce the risk of ambiguous references being provided.

.. autoclass:: ansys.grantami.bomanalytics.bom_types.AttributeReferenceBuilder
   :inherited-members:
   :member-order: by_mro_by_source
