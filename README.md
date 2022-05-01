# PgoOPS 运维平台

[![python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://github.com/yanshicheng/super_ops)
[![django](https://img.shields.io/badge/Django-3.2+-green.svg)](https://github.com/yanshicheng/super_ops)
[![django](https://img.shields.io/badge/django_rest_framework-Latest-green.svg)](https://github.com/yanshicheng/super_ops)
[![mysql](https://img.shields.io/badge/Mysql-5.7+-green.svg)](https://github.com/yanshicheng/super_ops)

# 简介 

PgoOps 运维平台, 主要针对复杂的, 需求不一的业务环境, 构建一套兼容性比较强的运维自动化平台，目前平台正在逐步开发阶段。详细信息可以看后面的核心功能简介。

​	平台后端使用:`django + drf`, 平台前端使用:`vue-element-admin` 进行二次开发.

- [演示地址](http://www.pgoops.com)
- [部署文档](https://www.cnblogs.com/yanshicheng/p/16214938.html)

## 仓库地址

- [ 🌐 码云仓库后端地址](https://gitee.com/pgoops/pgoops)
- [ 🌐 码云仓库前端地址](https://gitee.com/pgoops/pgoops_web)

- [ 🌐 github仓库后端地址](https://github.com/yanshicheng/pgoops)
- [ 🌐 github仓库前端地址](https://github.com/yanshicheng/pgoops_web)

## 模块说明

- [x] **用户管理**: 通过 Django 原生的用户管理系统进行扩展。

- [x] **权限系统**

  - [x] API 权限: 基于casbin的RBAC权限控制
  - [x] 动态菜单: 采用了 element admin 的动态菜单，通过 django 控制对应角色返回的菜单。

- [x] **服务树**

  - [ ] 陆续优化

- [x] **数据字典**: 数据字典主要用于实现字段变化频繁或者对存储性能比较高的，可以自定义后端存储目前采用 Mysql。 

  - [x] CMDB: 基于数据字典实现。
      - [x] 前端 + 后端
      - [x] 日志记录
      - [x] Agent API
      - [x] Agent

- [x] **代码平台(ansible版本)** : 基于ansible 的即时代码平台，通过 celery 解决性能问题。

- [x] **消息中心**: 告警通知中心，通过 celery 解决性能问题。

    - 支持的通告媒介
        - [x] 邮件
        - [x] 钉钉
        - [x] 飞书
        - [ ] 短信(正在测试)
        - [ ] 语音电话

    - 支持接入的第三方平台
        - [x] prometheus
        - [ ] zabbix
        - [ ] jenkins

- [x] **调度平台**: 基于 django-celery-beat 实现

- [ ] 发布平台

- [ ] 监控配置中心

- [ ] 工单系统

## 项目界面展示

登陆页面

<p align="center">
  <img width="900" src="https://images.cnblogs.com/cnblogs_com/yanshicheng/2153942/o_220501191206_WechatIMG3599.png">
</p>

个人中心

<p align="center">
  <img width="900" src="https://images.cnblogs.com/cnblogs_com/yanshicheng/2153942/o_220501190344_iShot_2022-05-02_03.01.41.png">
</p>

数据字典

<p align="center">
  <img width="900" src="https://images.cnblogs.com/cnblogs_com/yanshicheng/2153942/o_220501190324_iShot_2022-05-02_03.00.14.png">
</p>

<p align="center">
  <img width="900" src="https://images.cnblogs.com/cnblogs_com/yanshicheng/2153942/o_220501190336_iShot_2022-05-02_03.00.28.png">
</p>

服务树

<p align="center">
  <img width="900" src="https://images.cnblogs.com/cnblogs_com/yanshicheng/2153942/o_220501185014_image.png">
</p>

代码平台

<p align="center">
  <img width="900" src="https://images.cnblogs.com/cnblogs_com/yanshicheng/2153942/o_220501185217_image.png">
</p>

<p align="center">
  <img width="900" src="https://images.cnblogs.com/cnblogs_com/yanshicheng/2153942/o_220501185420_image.png">
</p>

<p align="center">
  <img width="900" src="https://images.cnblogs.com/cnblogs_com/yanshicheng/2153942/o_220501190220_iShot_2022-05-02_02.57.59.png">
</p>

<p align="center">
  <img width="900" src="https://images.cnblogs.com/cnblogs_com/yanshicheng/2153942/o_220501190210_iShot_2022-05-02_02.57.35.png">
</p>

权限系统

<p align="center">
  <img width="900" src="https://images.cnblogs.com/cnblogs_com/yanshicheng/2153942/o_220501190310_iShot_2022-05-02_02.59.48.png">
</p>

消息中心

<p align="center">
  <img width="900" src="https://images.cnblogs.com/cnblogs_com/yanshicheng/2153942/o_220501190230_iShot_2022-05-02_02.58.42.png">
</p>

## 鸣谢

| 项目 |
| -------------------------------------------------- |
| [django](https://code.djangoproject.com/)                    |
| [django-rest-framework](https://www.django-rest-framework.org/) |
| [celery](https://docs.celeryq.dev/en/stable/)                |
| [vue](https://github.com/vuejs/vue)                          |
| [element-ui](https://github.com/ElemeFE/element) |
| [vue-element-admin](https://panjiachen.github.io/vue-element-admin-site/zh/) |
| [axios](https://github.com/axios/axios) |

## License

[MIT](https://gitee.com/super-ops/super_ops/blob/master/LICENSE)