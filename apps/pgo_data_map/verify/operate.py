from ..models import Classify, Fields, Asset, AssetBind, ClassifyBind
from django.db.models import Q
from collections import OrderedDict
from django.forms.models import model_to_dict


class OperateInstance:
    @staticmethod
    def get_classify(id):
        """通过ID 查找指定分类表"""
        return Classify.objects.filter(id=id).first()

    # 获取类型表的 子表
    @staticmethod
    def get_children_classify(p_tid):
        """通过 主表ID 查找 子分类表 pid=id"""
        children_classify = Classify.objects.filter(pid=p_tid)
        if children_classify:
            return children_classify
        return None

    @staticmethod
    def get_parent_classify_classify(pid):
        parent_classify_classify_obj = Classify.objects.filter(id=pid).first()
        if parent_classify_classify_obj:
            return parent_classify_classify_obj
        return None

    # parent_classify

    @staticmethod
    def get_parent_classify_bind(pid):
        """通过分类表主ID 查找 关系绑定表数据"""
        parent_bind_obj = ClassifyBind.objects.filter(parent_classify_id=pid)
        if parent_bind_obj:
            return parent_bind_obj
        return None

    @staticmethod
    def get_child_classify_bind(cid):
        """通过 child_classify_id 获取表关系记录"""
        child_classify_obj = ClassifyBind.objects.filter(child_classify_id=cid)
        if child_classify_obj:
            return child_classify_obj
        return None

    @staticmethod
    def get_classify_bind(pid, cid):
        """根据 parent_classify_id 和 child_classify_id 返回分类关系表"""
        classify_bind_obj = ClassifyBind.objects.filter(
            parent_classify_id=pid, child_classify_id=cid
        ).first()
        if classify_bind_obj:
            return classify_bind_obj
        return None

    @staticmethod
    def get_abs_asset_bind(p_id, c_id):
        """根据  parent_asset_id child_asset_id 查询 asset_bind 记录"""
        asset_bind = AssetBind.objects.filter(
            parent_asset_id=p_id, child_asset_id=c_id
        ).first()
        if asset_bind:
            return asset_bind
        return None

    @staticmethod
    def get_asset_bind(t_id):
        """
        根据 classify_bind_id 查找 资产绑定记录
        """
        asset_bind = AssetBind.objects.filter(classify_bind_id=t_id)
        if asset_bind:
            return asset_bind
        return None

    @staticmethod
    def get_parent_asset_bind(t_id, p_id):
        """根据 表关系ID 主资产ID,  获取资产数据"""
        asset_bind = AssetBind.objects.filter(classify_bind=t_id, parent_asset_id=p_id)
        if asset_bind:
            return asset_bind
        return None

    @staticmethod
    def get_child_asset_bind(t_id, c_id):
        """根据 表关系ID 子资产ID 获取资产数据"""
        asset_bind = AssetBind.objects.filter(
            classify_bind_id=t_id, child_asset_id=c_id
        )
        if asset_bind:
            return asset_bind
        return None

    @staticmethod
    def get_c_asset_bind(c_id):
        """根据 子资产ID 获取资产数据"""
        asset_bind = AssetBind.objects.filter(child_asset_id=c_id)
        if asset_bind:
            return asset_bind
        return None

    # @staticmethod
    # def create_asset(c_id, *args):
    #     asset_obj = Asset.objects.create(asset_key=get_md5(*args), classify_id_id=c_id)
    #     asset_obj.save()
    #     return asset_obj

    @staticmethod
    def get_asset(id):
        """根据 ID 获取资产记录"""
        asset_obj = Asset.objects.filter(id=id).first()
        if asset_obj:
            return asset_obj
        return None

    @staticmethod
    def get_classify_asset(id, cid):
        """根据 分类表ID 资产表 ID 获取资产数据"""
        asset_obj = Asset.objects.filter(id=id, classify_classify_id=cid).first()
        if asset_obj:
            return asset_obj
        return None

    @staticmethod
    def get_all_asset(s_id):
        asset_all_obj = Asset.objects.filter(classify_id=s_id)
        if asset_all_obj:
            return asset_all_obj
        return None

    @staticmethod
    def get_classify_field(c_id):
        """根据分类表ID返回 fields 字段表"""
        field_obj = Fields.objects.filter(classify_id=c_id).first()
        if field_obj:
            return field_obj

        return None

    @staticmethod
    def get_all_field_map(c_id):
        field_all = Classify.objects.filter(id=c_id).values()
        if field_all:
            return field_all
        return None

    @staticmethod
    def get_asset_bind_exists(c_id):
        """查询 parent_asset_id 或者 child_asset_id 等于指定id的资产"""
        field_all = AssetBind.objects.filter(
            Q(parent_asset_id=c_id) | Q(child_asset_id=c_id)
        )
        if field_all:
            return field_all
        return None

    @staticmethod
    def get_p_bind_asset(id, pid):
        """通过主资产ID 和 分类ID 查询关联下 所有的数据"""
        # 获取关联数据类型
        classify_bind = OperateInstance.get_parent_classify_bind(pid)
        l_c = []
        if classify_bind:
            for t_r in classify_bind:
                data = OrderedDict()
                asset_re_all = OperateInstance.get_parent_asset_bind(t_r.id, id)
                data["classify_name"] = t_r.child_classify.name
                data["classify_id"] = t_r.child_classify.id
                data["parent_classify_name"] = t_r.child_classify.pid.name
                data["fields"] = t_r.child_classify.fields.fields
                if asset_re_all:
                    data["data"] = [model_to_dict(i.child_asset) for i in asset_re_all]
                else:
                    data["data"] = []
                l_c.append(data)
            return l_c
        return []

    def get_c_bind_asset(id, cid):
        """通过子资产ID 和 分类ID 查询关联下 所有的数据"""
        # 查询到所有的关联表记录
        classify_bind = OperateInstance.get_child_classify_bind(cid)
        l_c = []
        if classify_bind:
            # 循环关联表记录
            for t_r in classify_bind:
                asset_re_all = OperateInstance.get_child_asset_bind(t_r.id, id)
                if not asset_re_all:
                    continue
                data = OrderedDict()
                data["classify_name"] = t_r.parent_classify.name
                data["classify_id"] = t_r.parent_classify.id
                data["parent_classify_name"] = t_r.parent_classify.pid.name
                data["fields"] = t_r.parent_classify.fields.fields
                if asset_re_all:
                    data["data"] = [model_to_dict(i.parent_asset) for i in asset_re_all]
                else:
                    data["data"] = []
                l_c.append(data)
            return l_c
        return []

    @staticmethod
    def get_p_classify_bind(pid):
        """根据 主 classify_id 返回所有 关联数据"""
        parent_bind_obj = ClassifyBind.objects.filter(parent_classify_id=pid)
        if parent_bind_obj:
            return parent_bind_obj
        return []

    def get_c_classify_bind(cid):
        """根据 子 classify_id 返回所有 关联数据"""
        parent_bind_obj = ClassifyBind.objects.filter(child_classify_id=cid)
        if parent_bind_obj:
            return parent_bind_obj
        return []
