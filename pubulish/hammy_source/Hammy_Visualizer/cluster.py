import numpy as np
import os
import json
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, davies_bouldin_score
from scipy.stats import spearmanr

TOL = 1e-6
np.set_printoptions(suppress=True, precision=2)

class VisualEntity:
    def __init__(self, entity_data):
        self.entity_data = entity_data
        
        self.is_valid = self.entity_data[0]
        self.bldg_id = self.entity_data[1]

        self.all_var = self.entity_data[3][:-1]
        self.geo_win_var = self.entity_data[3][:20]
        self.geo_var = self.entity_data[3][:18]
        self.form_var = self.entity_data[3][12:18]
        
        self.area = self.entity_data[4][1]
        self.form_factor = self.entity_data[4][12:15]
        self.perform = [self.entity_data[4][22], self.entity_data[4][27], self.entity_data[4][29]]
        self.geo_perform = self.geo_var + self.perform
        
        self.crit_ori = self.entity_data[5][0]
        self.crit_p = self.entity_data[5][1]
        self.iter_id = None
        self.rank_ori = None
        self.rank_p = None
        
        self.crit_to_show = None
        self.rank_to_show = None
        
        self.cluster_label = None
        self.feature_display = []


class Visualization:
    def __init__(self, log_folder, display_folder, attributes, record = True):
        self.record = record
        self.attributes = attributes
        self.visual_aim = attributes["visual_aim"]
        self.scope = attributes["scope"]
        self.rank_with_perform = attributes["rank_with_perform"]
        
        self.pca_dim = attributes["pca_dim"]
        self.var_name = attributes["var_name"]
        self.if_pca = attributes["if_pca"]
        
        self.n_clusters = attributes["n_clusters"]
        
        
        self.log_folder = log_folder
        self.display_folder = display_folder
        
        
        self.files = []
        self.log_data = []
        self.run_infos = {}
        self.crit_ori_base = None
        self.crit_p_base = None
        self.merge_log_files()
        
        self.all_entities = []
        self.entity_nr = None
        self.make_entity_objs()
        
        self.all_crits_p = []
        self.all_ranks_p = []
        self.make_rank()
        
        self.selected_entities = []
        self.selected_entity_nr = None
        self.variables = []
        self.features_cluster = []
        self.features_display = []
        self.select()
        self.get_features()

        self.sel_crits_ori = []
        self.sel_crits_p = []
        self.sel_ranks_ori = []
        self.sel_ranks_p = []
        self.crits_in_use = []
        self.ranks_in_use = []
        self.rerank_seleted()

        self.cluster_labels = []
        self.run_k_means()
        self.record_cluster_evaluation() 
        self.cluster_label_dict = {}
        self.get_cluster_label_dict()
        
        
        self.cluster_infos = []
        self.geo_infos = []
        self.relevances = []
        if self.visual_aim == "nebula":
            self.entities_to_show = self.selected_entities
        else:
            self.entities_to_show, self.relevances = self.get_bests()
            
        self.record_entity_infos()
        self.log_name = None
        self.res_log_path = None
        self.output_logs()



    @staticmethod
    def read_run_info(rank_with_perf, baseline_data):
        weight = baseline_data[8][2]["weight_gwp"]
        if abs(weight - 0.616) < TOL:
            crit_name = "Total Carbon"
        else:
            crit_name = "GWP : Energy = {} : {}".format(str(weight), str(1-weight))
        
        crit_ori, crit_p = baseline_data[5]
        crit_use = crit_ori if rank_with_perf else crit_p    
        p_assumpt = baseline_data[8][1]
        run_info = {
            "Criteria Item": crit_name,
            "Baseline Criteria": crit_ori, 
            "Baseline Criteria Penalized": crit_p, 
            "Baseline Criteria In Use": crit_use,
            "Settings": {
                "Plan Settings": baseline_data[8][0],
                "Penaty Assumptions": {
                    "min_size": p_assumpt[0],
                    "min_angle": p_assumpt[1],
                    "max_ct_area_gls": p_assumpt[2],
                    "max_ct_area_mass": p_assumpt[3],
                    "material_type": p_assumpt[4],
                    "min_sDA": p_assumpt[5],
                    "max_ASE": p_assumpt[6],
                    "daylight_calibration": p_assumpt[7]
                },
                "Criteria Attributes": baseline_data[8][2]
            },
            "Constraints and Requirements": {
                "area_req": baseline_data[7][0],
                "user_reqs": baseline_data[7][1]
            },
            "Baseline Info": baseline_data[:7]
        }
        
        return run_info
    
        
    def merge_log_files(self):
        for file in os.listdir(self.log_folder):
            if file.endswith(".json"):
                self.files.append(file)
                
        for file in self.files:
            file_path = os.path.join(self.log_folder, file)
            with open(file_path, "r") as f:
                run_data = json.load(f)
                if run_data != []:
                    run_name = file.split(".")[0]
                    self.run_infos[run_name] = Visualization.read_run_info(self.rank_with_perform, run_data[0])
                    self.crit_ori_base = run_data[0][5][0]
                    self.crit_p_base = run_data[0][5][1]
                    self.log_data.extend(run_data[1:])
                
        
    def make_entity_objs(self):
        for i, entity_data in enumerate(self.log_data):
            entity = VisualEntity(entity_data)
            entity.iter_id = i
            self.all_entities.append(entity)
        self.entity_nr = len(self.all_entities)
    
    
    def make_rank(self):
        self.all_crits_p = [e.crit_p for e in self.all_entities]
        self.all_ranks_p = np.asarray(self.all_crits_p).argsort().argsort().tolist()
        for e, r in zip(self.all_entities, self.all_ranks_p):
            e.rank_p = r
            
        
    def select(self):
        for e in self.all_entities:
            # just select entites better than baseline
            if self.scope == 0:
                if e.crit_p < self.crit_p_base:
                    self.selected_entities.append(e)    
            # select the first half & valid
            elif self.scope == 1:
                if e.rank_p <= 0.5 * self.entity_nr and e.is_valid:
                    self.selected_entities.append(e)
            else:
                if e.is_valid:
                    self.selected_entities.append(e)
                    
        self.selected_entity_nr = len(self.selected_entities)
    
    def rerank_seleted(self):
        self.sel_crits_ori = [e.crit_ori for e in self.selected_entities]
        self.sel_crits_p = [e.crit_p for e in self.selected_entities]
        
        self.sel_ranks_ori = np.asarray(self.sel_crits_ori).argsort().argsort().tolist()
        self.sel_ranks_p = np.asarray(self.sel_crits_p).argsort().argsort().tolist()
        
        if self.rank_with_perform:
            self.crits_in_use = self.sel_crits_ori
            self.ranks_in_use = self.sel_ranks_ori
        else:
            self.crits_in_use = self.sel_crits_p
            self.ranks_in_use = self.sel_ranks_p
            
        for i, e in enumerate(self.selected_entities):
            e.rank_ori = self.sel_ranks_ori[i]
            e.rank_p = self.sel_crits_p[i]
            e.crit_to_show = self.crits_in_use[i]
            e.rank_to_show = self.ranks_in_use[i]

                 
    @staticmethod
    def get_entity_var(var_name, entity):
        if var_name == "all_var":
            vars = entity.all_var
        elif var_name == "geo_win":
            vars = entity.geo_win_var
        elif var_name == "geo":
            vars = entity.geo_var
        elif var_name == "form":
            vars = entity.form_var
        elif var_name == "geo_perform":
            vars = entity.geo_perform
        return vars
    
    @staticmethod
    def normalize_data(data_to_norm):
        standard_scaler = StandardScaler()
        norm_data = standard_scaler.fit_transform(data_to_norm)
        return norm_data
    
    
    def get_features(self):

        for e in self.selected_entities:
            variables = Visualization.get_entity_var(self.var_name, e)
            self.variables.append(variables)
        features = Visualization.normalize_data(self.variables)
        
        pca = PCA(n_components=self.pca_dim)
        features_pca = pca.fit_transform(features)
        self.features_display = features_pca
        # if use pca for clustering
        if self.if_pca:
            self.features_cluster = features_pca
        else:
            self.features_cluster = features   
            

    def run_k_means(self):
        kmeans = KMeans(n_clusters=self.n_clusters)
        kmeans.fit(self.features_cluster)
        self.cluster_labels = kmeans.labels_
        
        for i, e in enumerate(self.selected_entities):
            e.cluster_label = int(self.cluster_labels[i])
            e.feature_display = self.features_display[i].tolist()
            
        # evaluations
        # Intrinsic metrics (lower, more compact)
        self.inertia = kmeans.inertia_
        # Silhouette Score (higher, better defined clusters)
        self.silhouette_avg = float(silhouette_score(self.features_cluster, self.cluster_labels))
        # Davies-Bouldin Index (lower, better separation)
        self.davies_bouldin = float(davies_bouldin_score(self.features_cluster, self.cluster_labels))
        
     
     
    def get_cluster_label_dict(self):
        for i, label in enumerate(self.cluster_labels):
            if label not in self.cluster_label_dict:
                self.cluster_label_dict[label] = []
            self.cluster_label_dict[label].append(i)
    
    
    
    @staticmethod
    def calc_variable_relevance(entities):
        
        features = []
        targets = []
        fea_tars = []
        for e in entities:
            features.append(e.all_var)
            targets.append(e.crit_to_show)
            fea_tars.append(e.all_var + [e.crit_to_show])
        
        features = np.asarray(features)
        targets = np.asarray(targets)
        fea_tars = np.asarray(fea_tars)
     
        variances = np.var(fea_tars, axis=0, ddof=1).round(2)
        # corr_with_crit = [spearmanr(features[:, i], targets).correlation for i in range(features.shape[1])]
        corr_with_crit = []
        for i in range(features.shape[1]):
            feature_column = features[:, i]
            if np.std(feature_column) == 0 or np.std(targets) == 0:
                corr_with_crit.append(0)
            else:
                corr_with_crit.append(spearmanr(feature_column, targets).correlation)
        corr_with_crit = np.abs(np.nan_to_num(corr_with_crit)).round(2)
        
        return variances.tolist()[:-1], corr_with_crit.tolist()

    
    def get_bests(self):
        cluster_labels = range(self.n_clusters)
        best_ids = []
        relevances = []
        for c in cluster_labels:
            entity_ids = self.cluster_label_dict[c]
            entity_in_cluster = []
            ranks_in_cluster = []
            for e_id in entity_ids:
                entity = self.selected_entities[e_id]
                rank = entity.rank_to_show
                entity_in_cluster.append(entity)
                ranks_in_cluster.append(rank)
            best_rank = min(ranks_in_cluster)
            best_id = entity_ids[ranks_in_cluster.index(best_rank)]
            best_ids.append(best_id)
            
            variances, correlation = self.calc_variable_relevance(entity_in_cluster)
            relevance = {
                "Cluster": c,
                "Variance": variances,
                "Correlation": correlation
            }
            relevances.append(relevance)
         
        entites_to_show = [self.selected_entities[i] for i in best_ids]
        return entites_to_show, relevances
     
        
    def record_cluster_evaluation(self):
        self.cluster_eva = self.attributes
        self.cluster_eva["inertia"] = self.inertia
        self.cluster_eva["silhouette_avg"] = self.silhouette_avg
        self.cluster_eva["davies_bouldin_index"] = self.davies_bouldin


    def record_entity_infos(self):
        for e in self.entities_to_show:
            cluster_info = [
                e.bldg_id,
                e.iter_id,
                e.cluster_label,
                e.feature_display,
                e.perform,
                [e.crit_to_show, e.rank_to_show]
            ],
            geo_info = [
                e.bldg_id, 
                e.iter_id,
                e.entity_data[2],
                e.entity_data[3],
                e.entity_data[4][0:2] + [e.entity_data[4][22], e.entity_data[4][27]] + e.entity_data[4][29:32],
                [e.crit_to_show, e.rank_to_show]
            ]

            self.cluster_infos.extend(cluster_info)
            self.geo_infos.append(geo_info)
        
    
    def output_logs(self):
        if not os.path.exists(self.display_folder):
            os.makedirs(self.display_folder)
        
        if_pca = "pca" if self.if_pca else "raw"
        scope = ["better", "half", "all"][self.scope]
        rank_strategy = "ori" if self.rank_with_perform else "p"
        self.log_name = "_".join(
            [
                self.visual_aim,
                scope,
                rank_strategy,
                self.var_name,
                str(self.pca_dim),
                if_pca,
                str(self.n_clusters)
            ]
        )
        
        res_log = [
            self.run_infos,
            self.cluster_infos,
            self.geo_infos,
            self.cluster_eva,
            self.relevances
        ]
        
        self.res_log_path = os.path.join(self.display_folder, "hammy_" + self.visual_aim, self.log_name + ".json")
        if self.record:
            with open(self.res_log_path, "w") as f:
                print("logging-----", self.res_log_path)
                json.dump(res_log, f, indent=4)