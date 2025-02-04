import os
import json
import pathlib
from datetime import datetime
from collections import OrderedDict


class ThemeUtils():
    """ Utils for Themes"""

    @staticmethod
    def load_themesconfig(app, handler):
        """Return themesconfig"""
        current_handler = handler()
        config_in_path = os.path.join(current_handler.config().get("input_config_path"), current_handler.tenant)
        tenant_config_path = os.path.join(config_in_path, 'tenantConfig.json')

        try:
            with open(tenant_config_path, encoding='utf-8') as fh:
                tenant_config = json.load(fh, object_pairs_hook=OrderedDict)
        except IOError as e:
            app.logger.error("Error reading tenantConfig.json: {}".format(
                e.strerror))
            return {}

        themes_config = tenant_config.get("themesConfig", None)

        if isinstance(themes_config, str):
            themes_config_path = themes_config
            try:
                if not os.path.isabs(themes_config_path):
                    themes_config_path = os.path.join(config_in_path, themes_config_path)
                with open(themes_config_path) as f:
                    themes_config = json.load(f)
            except:
                msg = "Failed to read themes configuration %s" % themes_config_path
                app.logger.error(msg)
                return {}
        elif not isinstance(themes_config, dict):
            msg = "Missing or invalid themes configuration in tenantConfig.json"
            app.logger.error(msg)
            return {}

        return themes_config

    @staticmethod
    def save_themesconfig(new_themes_config, app, handler):
        """Save themesconfig

        :param Dict new_themes_config: new themesConfig Dictionary
        :param Flask app: Flask application
        """
        current_handler = handler()
        config_in_path = os.path.join(current_handler.config().get("input_config_path"), current_handler.tenant)
        tenant_config_path = os.path.join(config_in_path, 'tenantConfig.json')

        try:
            with open(tenant_config_path, encoding='utf-8') as fh:
                tenant_config = json.load(fh, object_pairs_hook=OrderedDict)
        except IOError as e:
            app.logger.error("Error reading tenantConfig.json: {}".format(
                e.strerror))
            return False

        baksuffix = ".bak%s" % datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        themes_config = tenant_config.get("themesConfig", None)

        if isinstance(themes_config, str):
            themes_config_path = themes_config
            try:
                if not os.path.isabs(themes_config_path):
                    themes_config_path = os.path.join(config_in_path, themes_config_path)
                with open(themes_config_path) as f:
                    themes_config = json.load(f)

                with open(themes_config_path + baksuffix, "w", encoding="utf-8") as fh:
                    json.dump(themes_config, fh, indent=2, separators=(',', ': '))

                with open(themes_config_path, "w", encoding="utf-8") as fh:
                    json.dump(new_themes_config, fh, indent=2, separators=(',', ': '))

            except IOError as e:
                msg = "Failed to backup/save themes configuration %s: %s" % (themes_config_path, e.strerror)
                app.logger.error(msg)
                return False
        elif isinstance(themes_config, dict):
            try:
                with open(tenant_config_path + baksuffix, "w", encoding="utf-8") as fh:
                    json.dump(tenant_config, fh, indent=2, separators=(',', ': '))

                tenant_config["themesConfig"] = new_themes_config
                with open(tenant_config_path, "w", encoding="utf-8") as fh:
                    json.dump(tenant_config, fh, indent=2, separators=(',', ': '))
            except IOError as e:
                msg = "Failed to backup/save themes configuration %s: %s" % (tenant_config_path, e.strerror)
                app.logger.error(msg)
                return False
        else:
            msg = "Missing or invalid themes configuration in tenantConfig.json"
            app.logger.error(msg)
            return False

        return True

    @staticmethod
    def get_layers(app, handler):
        """Return geospatial file names from QGIS_RESOURCES_PATH"""
        current_handler = handler()
        resources_path = current_handler.config().get("qgs_resources_path")

        layers = []
        app.logger.info(resources_path)
        for ext in ['*.geojson', '*.kml', '*.gpkg', '*.shp']:
            for path in pathlib.Path(resources_path).rglob(ext):
                app.logger.info(str(path))
                app.logger.info(path.relative_to(resources_path))
                layer = str(path.relative_to(resources_path))
                if not layer.startswith("."):
                    layers.append(layer)
        return sorted(layers)

    @staticmethod
    def get_projects(app, handler):
        """Return QGIS project file names from QGIS_RESOURCES_PATH"""
        current_handler = handler()
        resources_path = current_handler.config().get("qgs_resources_path")
        ogc_service_url = current_handler.config().get("ogc_service_url")

        projects = []
        app.logger.info(resources_path)
        for path in pathlib.Path(resources_path).rglob("*.qgs"):
            app.logger.info(str(path))
            app.logger.info(path.relative_to(resources_path))
            project = str(path.relative_to(resources_path))[:-4].replace("\\", "/")
            url = ogc_service_url.rstrip("/") + "/" + project
            projects.append((url, project))
        return sorted(projects)

    @staticmethod
    def get_mapthumbs(app, handler):
        """Return mapthumbs from qwc2 assets path"""
        current_handler = handler()
        qwc2_path = current_handler.config().get("qwc2_path")
        mapthumbs = []
        thumbs_path = os.path.join(qwc2_path, "assets/img/mapthumbs")
        for mapthumb in os.listdir(thumbs_path):
            if not mapthumb.startswith("."):
                mapthumbs.append(mapthumb)
        mapthumbs.append("")
        return sorted(mapthumbs)

    @staticmethod
    def get_format():
        """Return image formats"""
        return (["", ""],
                ["jpg", "jpg"],
                ["jpeg", "jpeg"],
                ["image/jpeg", "image/jpeg"],
                ["image/png", "image/png"],
                ["image/png; mode=1bit", "image/png; mode=1bit"],
                ["image/png; mode=8bit", "image/png; mode=8bit"],
                ["image/png; mode=16bit", "image/png; mode=16bit"])

    @staticmethod
    def get_crs(app, handler):
        """Return coordinate systems"""
        current_handler = handler()
        tenant_qwc2_config = os.path.join(current_handler.config().get("input_config_path"), current_handler.tenant, "config.json")
        master_qwc2_config = os.path.join(current_handler.config().get("qwc2_path"), "config.json")

        qwc2_config = tenant_qwc2_config if os.path.isfile(tenant_qwc2_config) else master_qwc2_config

        with open(qwc2_config, encoding="utf-8") as fh:
            config = json.load(fh)
            if "projections" in config:
                projections = config["projections"]
                result = [["EPSG:3857", "EPSG:3857"]]
                for p in projections:
                    code = p["code"]
                    result.append([code, code])
                return tuple(result)
        return (["EPSG:3857", "EPSG:3857"],
                ["EPSG:4647", "EPSG:4647"],
                ["EPSG:25832", "EPSG:25832"])

    @staticmethod
    def get_default_search_providers(app, handler):
        """Return default search providers"""
        current_handler = handler()
        config_in_path = current_handler.config().get("input_config_path")
        tenantConfig = os.path.join(config_in_path, current_handler.tenant, 'tenantConfig.json')

        try:
            with open(tenantConfig, encoding="utf-8") as fh:
                config = json.load(fh)
                if "themesConfig" in config:
                    themes_config = config["themesConfig"]
                    if "defaultSearchProviders" in themes_config:
                        return themes_config["defaultSearchProviders"]
        except IOError as e:
            app.logger.error("Error reading tenantConfig.json: {}".format(
                e.strerror))

        return (["coordinates"])
