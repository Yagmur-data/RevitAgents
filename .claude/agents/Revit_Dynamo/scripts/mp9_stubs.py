# -*- coding: utf-8 -*-
"""mp9_stubs.py - a small FAKE Revit/Dynamo world for the offline logic test of MashProject9_v11.py (mp9_selftest.py).

Fakes only what the node calls: clr, Autodesk.Revit.DB (+ .ExtensibleStorage), RevitServices, System.Collections.Generic. It models the
rules the Revit API / V7 rely on, so a violation fails the test:
  * a PROJECT document has no FamilyCreate (InvalidOperationException) - Forms/ReferencePoints exist only in a family document
  * Document.Delete cascades like Revit (a ReferencePoint takes its CurveByPoints and their Forms with it; foreign elements that depend
    on a deleted element are deleted too and are reported in the returned ids -> the node must notice and roll back)
  * Transaction.RollBack restores everything (also deletions); creating/deleting outside a transaction raises
  * NewFormByCap creates, like Revit, ONE helper ReferencePoint per Form (Family4: 843 own + 1,499 helpers = 2,342); it needs one loop of 3 curve references; fault injection: W.fail_form_at (persistent from the n-th call),
    W.fail_form_all_reference (a profile made only of reference lines is rejected on the first try)
  * DataStorage names are limited to 255 characters
Proves control flow, counts, ids, files and JSON shape only - NOT pythonnet, NOT real Revit behaviour.
"""
import os
import types

F2M = 0.3048
OST_MASS = -2003400
OST_REFERENCE_POINTS = -2000710
OST_REFERENCE_LINES = -2000083
OST_SKETCH_LINES = -2000045
OST_MASS_FORM = -2003404
OST_DIMENSIONS = -2000260


class W(object):
    doc = None
    next_id = 1000
    commits = rollbacks = 0
    fail_form_at = None
    fail_form_all_reference = False
    reject_shared = False        # NewFormByCap raises when a profile curve is already used by an existing Form (Revit refusing a shared reference)
    commit_calls = 0
    commit_fail_at = None        # the n-th Transaction.Commit (1-based) fails: Revit rolls that transaction back and returns 'RolledBack'
    group_rollbacks = 0
    group_assimilated = 0
    transactions = []

    @classmethod
    def reset(cls, kind='mass', mass_category=True):
        cls.next_id = 1000
        cls.commits = cls.rollbacks = 0
        cls.fail_form_at = None
        cls.fail_form_all_reference = False
        cls.reject_shared = False
        cls.commit_calls = 0
        cls.commit_fail_at = None
        cls.group_rollbacks = cls.group_assimilated = 0
        cls.transactions = []
        cls.doc = FakeDoc(kind, mass_category)
        return cls.doc


def new_id():
    W.next_id += 1
    return W.next_id


class XYZ(object):
    def __init__(self, x, y, z):
        self.X, self.Y, self.Z = x, y, z


class ElementIdC(object):
    def __init__(self, v):
        self.Value = int(v)


def cat(value, name):
    return types.SimpleNamespace(Id=ElementIdC(value), Name=name)


class Element(object):
    is_type = False
    hidden = False             # True = a Revit-internal element that FilteredElementCollector does not return
    Category = None

    def __init__(self):
        self.Id = ElementIdC(new_id())
        self.UniqueId = 'uid-%d' % self.Id.Value
        self.IsValidObject = True
        self.depends = []          # elements this one depends on (cascade on delete)

    def GetType(self):
        return types.SimpleNamespace(Name=type(self).__name__)


class RefPoint(Element):
    def __init__(self, xyz):
        Element.__init__(self)
        self.Position = xyz
        self.Category = cat(OST_REFERENCE_POINTS, 'Reference Points')


class HelperPoint(RefPoint):
    """The extra ReferencePoint Revit creates for every Form (seen in Family4: id = Form id + 6). Deleted with its Form."""


class Curve(Element):
    def __init__(self, pts):
        Element.__init__(self)
        self.depends = list(pts)
        self.Category = cat(OST_REFERENCE_LINES, 'Reference Lines')
        self.IsReferenceLine = False
        self.GeometryCurve = types.SimpleNamespace(Reference=object())


class Form(Element):
    def __init__(self, curves):
        Element.__init__(self)
        self.depends = list(curves)
        self.Category = cat(OST_MASS_FORM, 'Form')


class Foreign(Element):
    """An element the user made (not ours); optionally depends on one of our points. Category default: Dimensions (= the user's work)."""
    def __init__(self, depends_on=None, category=(OST_DIMENSIONS, 'Dimensions')):
        Element.__init__(self)
        self.depends = [depends_on] if depends_on is not None else []
        self.Category = cat(*category) if category else None


class SketchPlane(Element):
    """Revit-internal element without a category that appears after the first run and depends on one of our points (not returned by collectors)."""
    hidden = True

    def __init__(self, depends_on):
        Element.__init__(self)
        self.depends = [depends_on]


class Storage(Element):
    def __init__(self, doc):
        Element.__init__(self)
        self.doc = doc
        self._name = ''

    @property
    def Name(self):
        return self._name

    @Name.setter
    def Name(self, v):
        if len(v) > 255:
            raise RuntimeError('name too long')
        self._name = v


class TypeEl(Element):
    is_type = True


class ArrayLike(list):
    def Append(self, x):
        self.append(x)


class ListC(list):
    @property
    def Count(self):
        return len(self)

    def Add(self, x):
        self.append(x)


class _ListFactory(object):
    def __class_getitem__(cls, t):
        return ListC


class Transaction(object):
    def __init__(self, doc, name=''):
        self.doc, self.name, self.status = doc, name, 'NotStarted'

    def Start(self):
        if self.doc.open_tx is not None:
            raise RuntimeError('nested transaction')
        self.doc.open_tx = self
        self.snap = self.doc.snapshot()
        self.status = 'Started'
        W.transactions.append(self.name)
        return 'Started'

    def Commit(self):
        W.commit_calls += 1
        if W.commit_fail_at is not None and W.commit_calls == W.commit_fail_at:
            self.doc.restore(self.snap)
            self.doc.open_tx = None
            self.status = 'RolledBack'
            W.rollbacks += 1
            return 'RolledBack'
        self.doc.open_tx = None
        self.status = 'Committed'
        W.commits += 1
        return 'Committed'

    def RollBack(self):
        self.doc.restore(self.snap)
        self.doc.open_tx = None
        self.status = 'RolledBack'
        W.rollbacks += 1

    def GetStatus(self):
        return self.status

    def GetFailureHandlingOptions(self):
        return types.SimpleNamespace(SetClearAfterRollback=lambda v: None, SetForcedModalHandling=lambda v: None)

    def SetFailureHandlingOptions(self, o):
        pass

    def Dispose(self):
        pass


class TransactionGroup(object):
    def __init__(self, doc, name=''):
        self.doc, self.name, self.status = doc, name, 'NotStarted'

    def Start(self):
        if getattr(self.doc, 'open_group', None) is not None:
            raise RuntimeError('nested group')
        self.doc.open_group = self
        self.snap = self.doc.snapshot()
        self.status = 'Started'
        W.transactions.append('GROUP ' + self.name)
        return 'Started'

    def Assimilate(self):
        if self.doc.open_tx is not None:
            raise RuntimeError('a transaction is still open')
        self.doc.open_group = None
        self.status = 'Committed'
        W.group_assimilated += 1
        return 'Committed'

    def RollBack(self):
        if self.doc.open_tx is not None:
            raise RuntimeError('a transaction is still open')
        self.doc.restore(self.snap)
        self.doc.open_group = None
        self.status = 'RolledBack'
        W.group_rollbacks += 1
        return 'RolledBack'

    def GetStatus(self):
        return self.status

    def Dispose(self):
        pass


class FamilyCreateC(object):
    def __init__(self, doc):
        self.doc = doc
        self.form_calls = 0

    def _need_tx(self):
        if self.doc.open_tx is None:
            raise RuntimeError('creating an element outside a transaction')

    def NewReferencePoint(self, xyz):
        self._need_tx()
        p = RefPoint(xyz)
        self.doc.add(p)
        return p

    def NewCurveByPoints(self, arr):
        self._need_tx()
        assert len(arr) == 2
        c = Curve(arr)
        self.doc.add(c)
        return c

    def NewFormByCap(self, solid, profile):
        self._need_tx()
        self.form_calls += 1
        if W.fail_form_at is not None and self.form_calls >= W.fail_form_at:
            raise RuntimeError('simulated NewFormByCap failure')
        if len(profile) != 3:
            raise RuntimeError('profile must be one closed loop of 3 curves')
        by_ref = {id(c.GeometryCurve.Reference): c for c in self.doc.elements.values() if isinstance(c, Curve)}
        curves = [by_ref[id(r)] for r in profile]
        if W.reject_shared:
            used = set(id(c) for f in self.doc.elements.values() if isinstance(f, Form) for c in f.depends)
            if any(id(c) in used for c in curves):
                raise RuntimeError('simulated: Revit refuses a curve that already bounds another Form')
        if W.fail_form_all_reference and all(c.IsReferenceLine for c in curves):
            raise RuntimeError('simulated: profile made only of reference lines')
        f = Form(curves)
        self.doc.add(f)
        h = HelperPoint(XYZ(0.0, 0.0, 0.0))
        h.depends = [f]
        self.doc.add(h)
        return f


class FakeDoc(object):
    def __init__(self, kind, mass_category=True):
        self.kind = kind
        self.IsFamilyDocument = (kind == 'mass')
        self.Title = 'Family1' if kind == 'mass' else 'Project1'
        self.elements = {}
        self.open_tx = None
        self.open_group = None
        self.Application = types.SimpleNamespace(ShortCurveTolerance=0.00256)
        cat = types.SimpleNamespace(Id=ElementIdC(OST_MASS if mass_category else -2000151), Name='Mass' if mass_category else 'Generic Models')
        self.OwnerFamily = types.SimpleNamespace(FamilyCategory=cat) if kind == 'mass' else None
        self._fc = FamilyCreateC(self)
        for _ in range(3):
            t = TypeEl()
            self.elements[t.Id.Value] = t

    @property
    def FamilyCreate(self):
        if not self.IsFamilyDocument:
            raise RuntimeError('InvalidOperationException: Document.FamilyCreate is not available in a project document')
        return self._fc

    def add(self, e):
        self.elements[e.Id.Value] = e

    def snapshot(self):
        return dict(self.elements)

    def restore(self, snap):
        self.elements = dict(snap)

    def Regenerate(self):
        pass

    def GetElement(self, eid):
        return self.elements.get(eid.Value)

    def Delete(self, arg):
        if self.open_tx is None:
            raise RuntimeError('modifying the document outside a transaction')
        wanted = list(arg) if isinstance(arg, (list, tuple)) else [arg]
        gone = set(e.Value for e in wanted)
        changed = True
        while changed:                               # cascade: dependents of deleted elements go too
            changed = False
            for el in list(self.elements.values()):
                if el.Id.Value not in gone and any(d.Id.Value in gone for d in el.depends):
                    gone.add(el.Id.Value)
                    changed = True
        for i in gone:
            self.elements.pop(i, None)
        return [ElementIdC(i) for i in sorted(gone)]

    def storages(self):
        return [e for e in self.elements.values() if isinstance(e, Storage)]

    def points(self):
        return [e for e in self.elements.values() if type(e) is RefPoint]

    def helper_points(self):
        return [e for e in self.elements.values() if isinstance(e, HelperPoint)]

    def curves(self):
        return [e for e in self.elements.values() if isinstance(e, Curve)]

    def forms(self):
        return [e for e in self.elements.values() if isinstance(e, Form)]


class Collector(object):
    """Fluent like Revit's: OfClass / WhereElementIs... return the collector itself; iterable; Dispose()."""
    def __init__(self, doc, view_id=None):
        self.doc = doc
        self.types = None
        self.cls = None
        self.category = None

    def OfClass(self, cls):
        self.cls = cls
        return self

    def OfCategory(self, cat):
        self.category = cat
        return self

    def GetElementCount(self):
        if self.category == OST_REFERENCE_POINTS:
            return len([e for e in self.doc.elements.values() if isinstance(e, RefPoint)])
        return 0

    def __iter__(self):
        if self.cls is DataStorageC:
            return iter(self.doc.storages())
        return iter([])

    def WhereElementIsNotElementType(self):
        self.types = False
        return self

    def WhereElementIsElementType(self):
        self.types = True
        return self

    def ToElementIds(self):
        return [ElementIdC(e.Id.Value) for e in self.doc.elements.values() if e.is_type == bool(self.types) and not e.hidden]

    def Dispose(self):
        pass


class DataStorageC(object):
    @staticmethod
    def Create(doc):
        if doc.open_tx is None:
            raise RuntimeError('creating an element outside a transaction')
        s = Storage(doc)
        doc.add(s)
        return s


def build_stubs():
    m = {}
    clr = types.ModuleType('clr')
    clr.AddReference = lambda n: None
    m['clr'] = clr
    db = types.ModuleType('Autodesk.Revit.DB')
    db.XYZ, db.ElementId = XYZ, ElementIdC
    db.BuiltInCategory = types.SimpleNamespace(OST_Mass=OST_MASS, OST_ReferencePoints=OST_REFERENCE_POINTS, OST_ReferenceLines=OST_REFERENCE_LINES,
                                               OST_SketchLines=OST_SKETCH_LINES, OST_MassForm=OST_MASS_FORM)
    db.FilteredElementCollector = Collector
    db.UnitUtils = types.SimpleNamespace(ConvertToInternalUnits=lambda v, u: v / F2M)
    db.UnitTypeId = types.SimpleNamespace(Meters='m')
    db.Transaction = Transaction
    db.TransactionGroup = TransactionGroup
    db.TransactionStatus = types.SimpleNamespace(Started='Started', Committed='Committed', RolledBack='RolledBack')
    db.ReferencePointArray, db.ReferenceArray = ArrayLike, ArrayLike
    es = types.ModuleType('Autodesk.Revit.DB.ExtensibleStorage')
    es.DataStorage = DataStorageC
    # the node uses isinstance-free collectors; OfClass(DataStorage) must hand back the Storage list
    db.DataStorage = DataStorageC
    gen = types.ModuleType('System.Collections.Generic')
    gen.List = _ListFactory
    for name in ('Autodesk', 'Autodesk.Revit', 'System'):
        m[name] = types.ModuleType(name)
    m['Autodesk.Revit.DB'] = db
    m['Autodesk.Revit.DB.ExtensibleStorage'] = es
    m['System.Collections.Generic'] = gen
    rs = types.ModuleType('RevitServices')
    rp = types.ModuleType('RevitServices.Persistence')
    rt = types.ModuleType('RevitServices.Transactions')

    class DM(object):
        @property
        def CurrentDBDocument(self):
            return W.doc

    class TM(object):
        def EnsureInTransaction(self, doc):
            doc.open_tx = 'dynamo'

        def TransactionTaskDone(self):
            if W.doc.open_tx == 'dynamo':
                W.doc.open_tx = None

        def ForceCloseTransaction(self):
            if W.doc.open_tx == 'dynamo':
                W.doc.open_tx = None
    rp.DocumentManager = types.SimpleNamespace(Instance=DM())
    rt.TransactionManager = types.SimpleNamespace(Instance=TM())
    m['RevitServices'], m['RevitServices.Persistence'], m['RevitServices.Transactions'] = rs, rp, rt
    return m
