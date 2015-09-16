from django_migration_testcase import MigrationTest


class ExampleMigrationTest(MigrationTest):
    before = '0001_initial'
    after = '0002_mymodel_number'
    app_name = 'test_app'

    def test_migration(self):
        MyModel = self.get_model_before('MyModel')

        for i in range(10):
            mymodel = MyModel()
            mymodel.name = 'example name {}'.format(i)
            mymodel.save()
        self.assertEqual(MyModel.objects.count(), 10)

        self.run_migration()

        MyModel = self.get_model_before('MyModel')
        self.assertEqual(MyModel.objects.count(), 10)

    def test_invalid_field(self):
        MyModel = self.get_model_before('MyModel')
        mymodel = MyModel()
        mymodel.number = 10
        mymodel.save()

        mymodel = MyModel.objects.get()
        with self.assertRaises(AttributeError):
            mymodel.number

        self.run_migration()

        MyModel = self.get_model_after('MyModel')
        mymodel = MyModel.objects.get()
        self.assertEqual(mymodel.number, None)

        mymodel.number = 10
        mymodel.save()

        mymodel = MyModel.objects.get()
        self.assertEqual(mymodel.number, 10)


class AddDoubleNumberTest(MigrationTest):
    before = '0002_mymodel_number'
    after = '0003_mymodel_double_number'
    app_name = 'test_app'

    def test_migration(self):
        MyModel = self.get_model_before('MyModel')
        self.assertNotIn('double_number', MyModel._meta.get_all_field_names())

        self.run_migration()

        MyModel = self.get_model_after('MyModel')
        self.assertIn('double_number', MyModel._meta.get_all_field_names())


class MigrationsByNumberOnlyTest(MigrationTest):
    before = '0002'
    after = '0003'
    app_name = 'test_app'

    def test_migration(self):
        MyModel = self.get_model_before('MyModel')
        self.assertNotIn('double_number', MyModel._meta.get_all_field_names())

        self.run_migration()

        MyModel = self.get_model_after('MyModel')
        self.assertIn('double_number', MyModel._meta.get_all_field_names())


class PopulateDoubleNumberTest(MigrationTest):
    before = '0003_mymodel_double_number'
    after = '0004_populate_mymodel_double_number'
    app_name = 'test_app'

    def test_migration(self):
        MyModel = self.get_model_before('MyModel')

        MyModel = self.get_model_before('MyModel')

        for i in range(10):
            mymodel = MyModel()
            mymodel.name = 'example name {}'.format(i)
            mymodel.number = i
            mymodel.save()

        self.run_migration()

        MyModel = self.get_model_after('MyModel')
        for mymodel in MyModel.objects.all():
            self.assertEqual(mymodel.number * 2, mymodel.double_number)


class GetModelMigrationTest(MigrationTest):
    before = '0001_initial'
    after = '0002_mymodel_number'
    app_name = 'test_app'

    def test_migration(self):
        MyModel = self.get_model_before('test_app.MyModel')
        self.assertEqual(MyModel.__name__, 'MyModel')

        self.run_migration()

        MyModel = self.get_model_before('test_app.MyModel')
        self.assertEqual(MyModel.__name__, 'MyModel')


class ForeignKeyTest(MigrationTest):
    before = '0004_populate_mymodel_double_number'
    after = '0005_foreignmodel'
    app_name = 'test_app'

    def test_migration(self):
        MyModel = self.get_model_before('test_app.MyModel')
        self.assertEqual(MyModel.__name__, 'MyModel')

        self.run_migration()

        ForeignModel = self.get_model_after('test_app.ForeignModel')
        self.assertEqual(ForeignModel.__name__, 'ForeignModel')

        MyModel = self.get_model_after('test_app.MyModel')
        self.assertEqual(MyModel.__name__, 'MyModel')

        my = MyModel(name='test_my', number=1, double_number=3.14)
        my.save()

        foreign = ForeignModel(name='test_foreign', my=my)

    def test_migration2(self):
        """Same test as test_migration, but this one passes."""
        MyModel = self.get_model_before('test_app.MyModel')
        self.assertEqual(MyModel.__name__, 'MyModel')

        self.run_migration()

        ForeignModel = self.get_model_after('test_app.ForeignModel')
        self.assertEqual(ForeignModel.__name__, 'ForeignModel')

        # get_model_before/get_model_after seems to not get the same model as
        # this crazy thing.
        MyModel = ForeignModel.my.field.rel.to
        self.assertEqual(MyModel.__name__, 'MyModel')

        my = MyModel(name='test_my', number=1, double_number=3.14)
        my.save()

        foreign = ForeignModel(name='test_foreign', my=my)

    def test_migration_clearly(self):
        """A clear illustration of the problem."""
        self.run_migration()

        ForeignModel = self.get_model_after('test_app.ForeignModel')

        # get_model_before/get_model_after seems to not get the same model as
        # this crazy thing.
        MyModel = ForeignModel.my.field.rel.to
        MyModel2 = self.get_model_after('test_app.MyModel')

        self.assertEqual(MyModel, MyModel2)
