# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'TourConfig.server_poll_range'
        db.add_column(u'tour_config_tourconfig', 'server_poll_range',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=5),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'TourConfig.server_poll_range'
        db.delete_column(u'tour_config_tourconfig', 'server_poll_range')


    models = {
        u'tour_config.tourconfig': {
            'Meta': {'object_name': 'TourConfig'},
            'dcs_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'gcm_sender_id': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_cancelled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'location_polling_rate': ('django.db.models.fields.PositiveIntegerField', [], {'default': '45'}),
            'max_tour_time': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'server_poll_range': ('django.db.models.fields.PositiveIntegerField', [], {'default': '5'}),
            'server_polling_rate': ('django.db.models.fields.PositiveIntegerField', [], {'default': '600'}),
            'start_time': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'tour_id': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '64'}),
            'tour_logo': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'tour_name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'tour_organization': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'tour_route': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tour_config.TourRoute']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'})
        },
        u'tour_config.tourroute': {
            'Meta': {'object_name': 'TourRoute'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'route': ('django.contrib.gis.db.models.fields.MultiLineStringField', [], {})
        }
    }

    complete_apps = ['tour_config']