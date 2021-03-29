from esgcet.mapfile import ESGPubMapConv
from esgcet.mkd_non_nc import ESGPubMKDNonNC
from esgcet.update import ESGPubUpdate
from esgcet.index_pub import ESGPubIndex


class BasePublisher(object):

    def __init__(self, argdict):
        self.argdict = argdict
        self.fullmap = argdict["fullmap"]
        self.silent = argdict["silent"]
        self.verbose = argdict["verbose"]
        self.cert = argdict["cert"]
        self.index_node = argdict["index_node"]
        self.data_node = argdict["data_node"]
        self.data_roots = argdict["data_roots"]
        self.globus = argdict["globus"]
        self.dtn = argdict["dtn"]
        self.replica = argdict["replica"]
        self.proj = ardict["proj"]
        self.json_file = argdict["json_file"]

    def cleanup(self):
        pass

    def mapfile(self):

        mapconv = ESGPubMapConv(self.fullmap)
        map_json_data = None
        try:
            map_json_data = mapconv.mapfilerun()

        except Exception as ex:
            print("Error with converting mapfile: " + str(ex), file=sys.stderr)
            self.cleanup()
            exit(1)
        return map_json_data

    def mk_dataset(self, map_json_data):
        mkd = ESGPubMKDNonNC(self.data_node, self.index_node, self.replica, self.globus, self.data_roots, self.dtn,
                                self.silent, self.verbose)
        try:
            out_json_data = mkd.run(map_json_data, "", self.json_file)
        except Exception as ex:
            print("Error making dataset: " + str(ex), file=sys.stderr)
            self.cleanup()
            exit(1)
        return out_json_data

    def update(self, json_data):
        up = ESGPubUpdate(self.index_node, self.cert, silent=self.silent, verbose=self.verbose)
        try:
            up.run(json_data)
        except Exception as ex:
            print("Error updating: " + str(ex), file=sys.stderr)
            self.cleanup()
            exit(1)

    def index_pub(self,dataset_records):
        ip = ESGPubIndex(self.index_node, self.cert, silent=self.silent, verbose=self.verbose)
        try:
            ip.do_publish(dataset_records)
        except Exception as ex:
            print("Error running index pub: " + str(ex), file=sys.stderr)
            self.cleanup()
            exit(1)

    def workflow(self):

        # step one: convert mapfile
        if not self.silent:
            print("Converting mapfile...")
        map_json_data = self.mapfile()

        # step two: make dataset
        if not self.silent:
            print("Done.\nMaking dataset...")
        out_json_data = self.mk_dataset(map_json_data)

        if not self.silent:
            print("Done.\nUpdating...")
        self.update(out_json_data)

        if not silent:
            print("Done.\nRunning index pub...")
        self.index_pub(out_json_data)

        if not silent:
            print("Done.")

