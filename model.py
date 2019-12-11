# -*- coding: utf-8 -*-
#########################################################
# python
import os
import traceback
import json
from datetime import datetime

# third-party

# sjva 공용
from framework import db, app, path_app_root

# 패키지
from .plugin import logger, package_name


db_file = os.path.join(path_app_root, 'data', 'db', '%s.db' % package_name)
app.config['SQLALCHEMY_BINDS'][package_name] = 'sqlite:///%s' % (db_file)

class ModelSetting(db.Model):
    __tablename__ = 'plugin_%s_setting' % package_name
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    __bind_key__ = package_name

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.String, nullable=False)
 
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __repr__(self):
        return repr(self.as_dict())

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}

    @staticmethod
    def get(key):
        try:
            return db.session.query(ModelSetting).filter_by(key=key).first().value.strip()
        except Exception as e:
            logger.error('Exception:%s %s', e, key)
            logger.error(traceback.format_exc())
    
    @staticmethod
    def set(key, value):
        try:
            item = db.session.query(ModelSetting).filter_by(key=key).with_for_update().first()
            if item is not None:
                item.value = value.strip()
                db.session.commit()
            else:
                db.session.add(ModelSetting(key, value.strip()))
        except Exception as e:
            logger.error('Exception:%s %s', e, key)
            logger.error(traceback.format_exc())

#########################################################


class ModelWavveEpisode(db.Model):
    __tablename__ = 'plugin_%s_auto_episode' % package_name
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    __bind_key__ = package_name

    id = db.Column(db.Integer, primary_key=True)
    contents_json = db.Column(db.JSON)
    streaming_json = db.Column(db.JSON)
    created_time = db.Column(db.DateTime)

    channelname = db.Column(db.String)
    
    programid = db.Column(db.String)
    programtitle = db.Column(db.String)
    
    contentid = db.Column(db.String)
    releasedate = db.Column(db.String)
    episodenumber = db.Column(db.String)
    episodetitle = db.Column(db.String)
    quality = db.Column(db.String)

    vod_type = db.Column(db.String) #general onair
    image = db.Column(db.String)
    playurl = db.Column(db.String)
    
    filename = db.Column(db.String)
    duration = db.Column(db.Integer)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    download_time = db.Column(db.Integer)
    completed = db.Column(db.Boolean)
    user_abort = db.Column(db.Boolean)
    pf_abort = db.Column(db.Boolean)
    etc_abort = db.Column(db.Integer) #ffmpeg 원인 1, 채널, 프로그램
    ffmpeg_status = db.Column(db.Integer)
    temp_path = db.Column(db.String)
    save_path = db.Column(db.String)
    pf = db.Column(db.Integer)
    retry = db.Column(db.Integer)
    filesize = db.Column(db.Integer)
    filesize_str = db.Column(db.String)
    download_speed = db.Column(db.String)
    call = db.Column(db.String)

    def __init__(self, call, info, streaming):
        self.created_time = datetime.now()
        self.completed = False
        self.user_abort = False
        self.pf_abort = False
        self.etc_abort = 0
        self.ffmpeg_status = -1
        self.pf = 0
        self.retry = 0
        self.call = call
        self.set_info(info)
        self.set_streaming(streaming)


    def __repr__(self):
        #return "<Episode(id:%s, episode_code:%s, quality:%s)>" % (self.id, self.episode_code, self.quality)
        return repr(self.as_dict())

    def as_dict(self):
        ret = {x.name: getattr(self, x.name) for x in self.__table__.columns}
        ret['created_time'] = self.created_time.strftime('%m-%d %H:%M:%S') if self.created_time is not None else ''
        ret['start_time'] = self.start_time.strftime('%m-%d %H:%M:%S') if self.start_time is not None else ''
        ret['end_time'] = self.end_time.strftime('%m-%d %H:%M:%S') if self.end_time is not None else ''
        return ret

    def set_info(self, data):
        self.contents_json = data
        self.channelname = data['channelname']
        
        self.programid = data['programid']
        self.programtitle = data['programtitle']
        
        self.contentid = data['contentid']
        self.releasedate = data['releasedate']
        self.episodenumber = data['episodenumber']
        self.episodetitle = data['episodetitle']
        self.image = 'https://' + data['image']
        self.vod_type = data['type']

    def set_streaming(self, data):
        self.streaming_json = data
        self.playurl = data['playurl']
        import framework.wavve.api as Wavve
        self.filename = Wavve.get_filename(self.contents_json, data['quality'])
        self.quality = data['quality']