import json
from datetime import datetime
import traceback

class ESGPubMapConv:

    def __init__(self, mapfilename, project=None, normalize=False, silent=False):

        self.mapfilename = mapfilename
        self.project = project
        self.normalize = normalize
        self.map_data_arr = []
        self.map_json = {}
        self.silent = silent

    def normalize_path(self, path):
        pparts = path.split('/')
        idx = pparts.index(self.project)
        if idx < 0:
            raise(BaseException("Incorrect Project in File Path!"))
        proj_root = '/'.join(pparts[0:idx])
        return('/'.join(pparts[idx:]), proj_root)

    def parse_map(self):
        """  """
        ret = []
        for line in self.map_data:

            parts = line.rstrip().split(' | ')
            if self.normalize:
                parts[1] = self.normalize_path(parts[1])

            ret.append(parts)

        self.map_data_arr = ret
        return ret

    def set_map_arr(self, maparr):
        self.map_data_arr = maparr

    def parse_map_arr(self):
        ''' Input: Takes a 2-D array representation of the parsed map.
        Returns: file records.  assumes that the files all belong to the same dataset
        '''
        if len(self.map_data_arr) == 0 and not self.silent:
            print("WARNING: empty map data")

        ret = []
        for lst in self.map_data_arr:
            rec = {}
            rec['file'] = lst[1]
            rec['size'] = int(lst[2])
            for x in lst[3:]:
                parts = x.split('=')
                if parts[0] == 'mod_time':
                    rec["timestamp"] = datetime.utcfromtimestamp(float(parts[1])).isoformat()[0:19] + "Z"
                    assert(rec["timestamp"].find('.') == -1)
                else:
                    rec[parts[0]] = parts[1]
            ret.append(rec)
        return ret

    def load_map_json(self):
        try:
            self.map_json = json.load(open(self.mapfilename))
        except:
            print(f"Error opening json data {self.mapfilename}")
            traceback.print_exc()

    def map_entry(self, project, fs_root):
        norm_path = self.normalize_path(self.map_json['file'])
        abs_path = "{}/{}".format(fs_root, norm_path)
        outarr = []

        outarr.append(self.map_json['id'])
        outarr.append(abs_path)
        outarr.append(self.map_json['size'])
        for x in self.map_json:
            if not x in ['id', 'file', 'size']:
                outarr.append("{}={}".format(x,self.map_json[x]))
        return ' | '.join(outarr)


    def mapfilerun(self):

        with open(self.mapfilename) as self.map_data:
            ret = self.parse_map()

        return ret
