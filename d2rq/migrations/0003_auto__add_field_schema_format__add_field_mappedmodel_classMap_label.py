# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Schema.format'
        db.add_column('d2rq_schema', 'format', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True), keep_default=False)

        # Adding field 'MappedModel.classMap_label'
        db.add_column('d2rq_mappedmodel', 'classMap_label', self.gf('django.db.models.fields.SlugField')(db_index=True, default='', max_length=50, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Schema.format'
        db.delete_column('d2rq_schema', 'format')

        # Deleting field 'MappedModel.classMap_label'
        db.delete_column('d2rq_mappedmodel', 'classMap_label')


    models = {
        'd2rq.mappedfield': {
            'Meta': {'object_name': 'MappedField'},
            'field_name': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['d2rq.MappedModel']"}),
            'rdf_proprety': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['d2rq.SchemaProperty']", 'null': 'True'})
        },
        'd2rq.mappedmodel': {
            'Meta': {'object_name': 'MappedModel'},
            'classMap_label': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'rdf_class': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['d2rq.SchemaClass']", 'null': 'True'})
        },
        'd2rq.schema': {
            'Meta': {'object_name': 'Schema'},
            'format': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'prefix': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'd2rq.schemaclass': {
            'Meta': {'object_name': 'SchemaClass'},
            'class_label': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'class_name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'schema': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['d2rq.Schema']"})
        },
        'd2rq.schemaproperty': {
            'Meta': {'object_name': 'SchemaProperty'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'prop_label': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'prop_name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'schema': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['d2rq.Schema']"})
        }
    }

    complete_apps = ['d2rq']
