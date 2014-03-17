# Copyright 2014 - Rackspace US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import uuid

import sqlalchemy as sa
from sqlalchemy import orm

from solum.objects import compiler_versions as abs_cv
from solum.objects import language_pack as abstract
from solum.objects import os_platform as abs_op
from solum.objects import registry
from solum.objects.sqlalchemy import models as sql
from solum.openstack.common.db import exception as db_exc


class LanguagePack(sql.Base, abstract.LanguagePack):
    """Represent a language pack in sqlalchemy."""

    __resource__ = 'language_packs'
    __tablename__ = 'language_pack'
    __table_args__ = sql.table_args()

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    uuid = sa.Column(sa.String(36), nullable=False)
    name = sa.Column(sa.String(100))
    description = sa.Column(sa.String(255))
    project_id = sa.Column(sa.String(36))
    user_id = sa.Column(sa.String(36))
    language_implementation = sa.Column(sa.String(100))
    language_pack_type = sa.Column(sa.String(100))
    tags = sa.Column(sa.Text)
    compiler_versions = orm.relationship("CompilerVersions",
                                         backref=__tablename__)
    os_platform = orm.relationship("OSPlatform",
                                   backref=__tablename__)
    attr_blob = sa.Column(sql.JSONEncodedDict(255))
    service_id = sa.Column(sa.Integer, sa.ForeignKey('service.id'),
                           nullable=False)

    def create(self, context):
        session = sql.Base.get_session()
        try:
            with session.begin(subtransactions=True):
                lp_service = registry.Service.get_first_by_type(
                    context, 'language_pack')
                if not lp_service:
                    lp_service = registry.Service()
                    lp_service.uuid = str(uuid.uuid4())
                    lp_service.name = 'language_pack service'
                    lp_service.service_type = 'language_pack'
                    lp_service.user_id = context.user
                    lp_service.project_id = context.tenant
                    lp_service.create(context)
                self.service_id = lp_service.id
                session.add(self)
        except db_exc.DBDuplicateEntry:
            self.__class__._raise_duplicate_object()


class CompilerVersions(sql.Base, abs_cv.CompilerVersions):

    __tablename__ = 'compiler_versions'
    __table_args__ = sql.table_args()

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    uuid = sa.Column(sa.String(36), nullable=False)
    version = sa.Column(sa.String(36), nullable=False)
    language_pack_id = sa.Column(sa.Integer, sa.ForeignKey('language_pack.id'),
                                 nullable=False)


class OSPlatform(sql.Base, abs_op.OSPlatform):

    __tablename__ = 'os_platform'
    __table_args__ = sql.table_args()

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    uuid = sa.Column(sa.String(36), nullable=False)
    os = sa.Column(sa.String(36), nullable=False)
    version = sa.Column(sa.String(36), nullable=False)
    language_pack_id = sa.Column(sa.Integer, sa.ForeignKey('language_pack.id'),
                                 nullable=False)


class LanguagePackList(abstract.LanguagePackList):
    """Represent a list of language packs in sqlalchemy."""

    @classmethod
    def get_all(cls, context):
        return LanguagePackList(sql.model_query(context, LanguagePack))
