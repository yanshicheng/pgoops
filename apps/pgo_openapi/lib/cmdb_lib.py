from apps.pgo_data_map.models import Classify, Fields, Asset, ClassifyBind, AssetBind
from apps.pgo_data_map.verify.check_data import check_data
from apps.pgo_data_map.verify.record_log import record


class CmdbHandle:
    def __init__(self, data, instance):
        self.data = data
        self.instance = instance

    def parent_classify(self):
        classify_obj, new_classify_data = self.get_classify()
        guid_fields = self.get_field_guid(classify_obj)
        old_classify_obj = self.get_asset(
            classify_obj, new_classify_data["data"][guid_fields]
        )
        if old_classify_obj:
            # 更新
            data = check_data(new_classify_data, old_classify_obj)
            return self.updata_asset_data(old_classify_obj, data)
        else:
            # 新增
            new_classify_data = check_data(new_classify_data, None)
            return self.create_asset_data(new_classify_data)

    def children_classify(self):
        for alias, data in self.data.items():
            classify = self.get_abs_classify(alias)
            c_classify = self.get_field_guid(classify)
            if classify:
                temp_data = []
                for i in data:
                    temp_data.append({"data": i, "classify": classify.id})

                all_bind_asset, classify_bind = self.get_asset_all(
                    self.instance, classify
                )
                self.diff_asset(all_bind_asset, temp_data, c_classify, classify_bind)

    def get_abs_classify(self, val):
        classify_obj = Classify.objects.filter(alias=val).first()
        if classify_obj:
            return classify_obj

    def get_classify(self):
        tmp_dic = {}
        if not self.data:
            raise KeyError("主模型数据不能为空.")
        parent_alias = list(self.data.keys())[0]
        parent_data = self.data[parent_alias]
        classify_obj = Classify.objects.filter(alias=parent_alias).first()
        if classify_obj and parent_data:
            tmp_dic["data"] = parent_data
            tmp_dic["classify"] = classify_obj.id
            return classify_obj, tmp_dic
        else:
            raise KeyError(f"找不到名为: f{parent_alias} 模型数据" )

    def get_field_guid(self, classify_obj):
        classify_field = Fields.objects.filter(classify=classify_obj).first()
        if classify_field:
            for k, v in classify_field.fields.items():
                if v.get("guid"):
                    return k
        else:
            raise KeyError("找不到指定的字段表")

    def get_asset_all(self, p_obj, c_obj):
        asset_bind_list = []
        classify_bind = ClassifyBind.objects.filter(
            parent_classify=p_obj.classify, child_classify=c_obj
        ).first()
        if classify_bind:
            asset_bind = AssetBind.objects.filter(
                classify_bind=classify_bind, parent_asset=self.instance
            )
            if asset_bind:
                for inc in asset_bind:
                    asset_bind_list.append(inc.child_asset)
        return asset_bind_list, classify_bind

    def diff_asset(self, asset_list, new_data, guid_name, classify_bind):
        update_list = []
        for new_asset in new_data:
            try:
                check_data(new_asset, None)
            except Exception:
                continue
            if asset_list:
                for n_a in asset_list:
                    if n_a.data[guid_name] == new_asset["data"][guid_name]:
                        update_list.append((n_a, new_asset))
                        asset_list.remove(n_a)
                        break
                else:
                    new_obj = self.create_asset_data(new_asset)
                    self.bind_asset(new_obj, classify_bind)
            else:
                # 新增
                new_obj = self.create_asset_data(new_asset)
                self.bind_asset(new_obj, classify_bind)
        # 删除
        for i in asset_list:
            self.delete_asset(i)

        # 更新
        for asset_tup in update_list:
            self.updata_asset_data(asset_tup[0], asset_tup[1])

    def get_asset(self, classify_obj, data):

        asset_obj = Asset.objects.filter(
            classify=classify_obj, data__icontains=data
        ).first()
        if asset_obj:
            return asset_obj
        return None

    def create_asset_data(self, data):
        new_asset = Asset.objects.create(
            data=data["data"], classify_id=data["classify"]
        )
        new_asset.save()
        return new_asset

    def updata_asset_data(self, obj, new_data):
        record("update_data", None, obj, new_data)
        obj.data = new_data["data"]
        obj.save()
        return obj

    def bind_asset(self, new_obj, classify_bind):
        new_bind = AssetBind.objects.create(
            parent_asset=self.instance,
            child_asset=new_obj,
            classify_bind=classify_bind,
        )
        record("bind", self.instance, new_obj, None)
        new_bind.save()

    def delete_asset(self, obj):
        record("delete_data", obj, None, None)
        obj.delete()


def cmdb(func, data, ins):
    cmdb_obj = CmdbHandle(data, ins)
    return getattr(cmdb_obj, func)()
