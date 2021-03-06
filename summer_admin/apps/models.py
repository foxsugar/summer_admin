from django.db import models


class Agent_user(models.Model):
    id = models.AutoField('id', primary_key=True)
    username = models.CharField('姓名', max_length=255, default='')
    password = models.CharField('密码', max_length=200, default='')
    invite_code = models.CharField('邀请码', max_length=255, default='')
    real_name = models.CharField('真实姓名', max_length=255, default='')
    level = models.IntegerField('级别', default=0)
    parent_id = models.IntegerField('上级id', default=0)
    email = models.CharField('邮件', max_length=255, default='')
    create_time = models.DateTimeField('创建时间', auto_now=True)
    id_card = models.CharField('身份证', max_length=255, default='')
    cell = models.IntegerField('电话', default=0)
    area = models.CharField('所属区域', max_length=2000, default='')
    address = models.CharField('地址', max_length=2000, default='')
    money = models.FloatField('钱', default=0)
    gold = models.FloatField('点券', default=0)
    pay_deduct = models.FloatField('支付提成', default=0)
    share_deduct = models.FloatField('分享提成', default=0)
    parent_pay_deduct = models.FloatField('上级支付提成', default=0)
    parent_share_deduct = models.FloatField('上级分享提成', default=0)
    agent_info = models.TextField('代理返利信息', max_length=255, default='')
    agent_info_record = models.TextField('代理返利记录', default='')
    # 0:打折代理 1:返利代理
    agent_type = models.IntegerField('代理类型', default=0)

    class Meta:
        db_table = 'agent_user'
        verbose_name = '代理'
        verbose_name_plural = '代理'


class Users(models.Model):
    id = models.AutoField(primary_key=True)
    account = models.CharField(max_length=255, default='')
    ali_id = models.CharField(max_length=255, default='')
    cash = models.FloatField(default=0)
    gold = models.FloatField(default=0)
    money = models.FloatField(default=0)
    rebate = models.FloatField(default=0)
    email = models.CharField(max_length=2000, default='')
    father_id = models.CharField(max_length=255, default='')
    image = models.CharField(max_length=4000, default='')
    ip_config = models.CharField(max_length=255, default='')
    open_id = models.CharField(max_length=255, default='')
    password = models.CharField(max_length=255, default='')
    username = models.CharField(max_length=4000, default='')
    uuid = models.CharField(max_length=255, default='')
    last_login_date = models.DateTimeField(auto_now=True)
    regist_date = models.DateTimeField(auto_now=True)
    referee = models.IntegerField(default=0)
    sex = models.IntegerField(default=0)
    vip = models.IntegerField(default=0)
    user_info = models.TextField(default='')

    class Meta:
        db_table = 'users'
        verbose_name = '用户表'
        verbose_name_plural = '用户'
        managed = False

class Agent_charge(models.Model):
    id = models.AutoField(primary_key=True)
    agent_id = models.IntegerField('充值id', default=0)
    charge_src_agent = models.IntegerField('充值原代理id', default=0)
    charge_type = models.IntegerField('充值类型', default=0)
    charge_num = models.FloatField('充值数量', default=0)
    charge_time = models.DateTimeField('充值时间', auto_now=True)

    class Meta:
        db_table = 'agent_charge'
        verbose_name = '代理充值表表'
        verbose_name_plural = '代理充值'
        managed = True


class Constant(models.Model):
    id = models.AutoField(primary_key=True)
    init_money = models.IntegerField(default=0)
    share_money = models.IntegerField(default=0)
    black_list = models.TextField(default=0)
    apple_check = models.CharField(max_length=255, default='')
    download = models.CharField(max_length=255, default='')
    download2 = models.CharField(max_length=255, default='')
    marquee = models.CharField(max_length=255, default='')
    marquee1 = models.CharField(max_length=255, default='')
    marquee2 = models.CharField(max_length=255, default='')
    version_of_android = models.CharField(max_length=255, default='')
    version_of_ios = models.CharField(max_length=255, default='')
    access_code = models.CharField(max_length=255, default='')
    income1 = models.IntegerField(default=0)
    income2 = models.IntegerField(default=0)
    class Meta:
        db_table = 'constant'
        verbose_name = '常量表'
        verbose_name_plural = '常量表'
        managed = False

class Charge(models.Model):
    order_id = models.CharField(max_length=255, primary_key=True)
    # order_id = models.AutoField()
    createtime = models.DateTimeField('创建时间', auto_now=True)
    money = models.FloatField('充值金额', default='')
    money_point = models.FloatField('充值点数')
    origin = models.IntegerField(default=0)
    charge_type = models.IntegerField(default=0)
    recharge_source = models.CharField(max_length=255, default='')
    share_area = models.CharField(max_length=255, default='')
    share_content = models.CharField(max_length=255, default='')
    shareid = models.IntegerField(default=0)
    sign = models.CharField(max_length=255, default='')
    sp_ip = models.CharField(max_length=255, default='')
    status = models.IntegerField(default=0)
    userid = models.IntegerField(default=0)
    username = models.CharField(max_length=255, default='')
    transaction_id = models.CharField(max_length=255, default='')
    finish_time = models.CharField(max_length=255, default='')
    class Meta:
        db_table = 'charge'
        verbose_name = '充值记录表'
        verbose_name_plural = '充值记录表'
        managed = False


class Log_record(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    charge_rebate = models.FloatField(default=0)
    game_num_data = models.TextField(default='')
    gold_room_income_data = models.TextField(default='')
    online_data = models.TextField(default='')
    log_info = models.TextField(default='')
    class Meta:
        db_table = 'log_record'
        verbose_name = 'log记录表'
        verbose_name_plural = 'log记录表'
        managed = False