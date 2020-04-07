import sys, json
from mapfile import normalize_path

DRS = { 'CMIP6' : [ 'mip_era' , 'activity_drs','institution_id','source_id','experiment_id','member_id','table_id','variable_id','grid_label', 'version' ] }
GA = { 'CMIP6' : ['frequency',
                     'realm',
                     'product',
                     'nominal_resolution',
                     'source_type',
                     'grid',
                     'creation_date',
                     'variant_label',
                     'sub_experiment_id',
                     'further_info_url',
                     'activity_id',
                     'data_specs_version', 'title']}

DATA_NODE = "greyworm1-rh7.llnl.gov"
INDEX_NODE = "esgf-fedtest.llnl.gov"
ROOT = {'esgf_data': '/esg/data'}

def get_dataset(mapdata, scandata):

    parts = mapdata[0]['id'].split('.')

    key = parts[0]
    facets = DRS[key]
    d = {}
    for i, f in enumerate(facets):
        if f in scandata['dataset']:
            ga_val = scandata['dataset'][f]
            if not parts[i] == ga_val:
                print("WARNING: {} does not agree!".format(f))
        d[f] = parts[i]

    for val in GA[key]:
        if val in scandata['dataset']:
            d[val] = scandata['dataset'][val]


    d['data_node'] = DATA_NODE
    d['index_node'] = INDEX_NODE
    DRSlen = len(DRS[key])

    d['instance_id'] = '.'.join(parts[0:DRSlen])
    d['master_id'] = '.'.join(parts[0:DRSlen-1])
    d['id'] = instance_id + '|' + node
    if not 'title' in d:
        d['title'] = instance_id
    d['replica'] = 'false' # set replica
    d['latest'] = 'true'
    d['type'] = 'Dataset'
    d['project'] = key


#Just tracking id for now, other file-specific metadata
def get_fname_trid(scandata, project):

    ret = {}
    for rec in scandata:
        fullpath = rec["name"] 
        parts = fullpath.split('/')
        relpath = normalize_path(fullpath, project)
        ret[fullpath] = {"tracking_id": rec["tracking_id"], 
        "title": parts[-1], "rel_path": relpath}

    return ret

URL_Templates = ["https://{}/thredds/fileServer/{}/{}|application/netcdf|HTTPServer"]

def genUrls(proj_root, rel_path):
    return  [template.format(DATA_NODE, proj_root, rel_path) for template in URL_Templates]


def get_file(dataset_rec, mapdata, fn_trid, proj_root):
    ret = dataset_rec.copy()
    dataset_id = dataset_rec["id"]
    ret['type'] = "File"
    fullfn = mapdata['file']


    ret['id'] = "{}.{}".format(ret['instance_id'].fn_trid("title"))
    ret['title'] = fn_trid["title"]
    ret["dataset_id"] = dataset_id
    ret["tracking_id"] = fn_trid["tracking_id"]

    for kn in mapdata:
        if kn not in ("id", "path"):
            ret[kn] = mapdata[kn]

    ret["url"] = gen_urls(proj_root, fn_trid["rel_path"])

    return ret
    # need to match up the 

def iterate_files(dataset_rec, mapdata, scandata, proj_root):

    ret = []

    for maprec in mapdata:

        fullpath = maprec['file']
        scanrec = scandata[fullpath]
        ret.append(get_file())


def get_records(mapfilename, scanfilename, xattrfn={}):

    mapobj = json.load(open(mapfilename))
    scanobj = json.load(open(scanfilename))
    xattrobj = json.load(open(xattrfn))
    rec = get_dataset(mapobj, scanobj)
    for key in xattr:
        rec[key] = xattr[key]
    project = rec['project']
    ret = [rec] + iterate_files(rec, scanobj)
    return ret

def main(args):

    if (len(args) < 2):
        print("Missing required arguments!")
        exit(0)
    if len(args) > 2:

        ret = get_records(args[0], args[1], xattr=xargs[2])
        print(json.dumps(ret, indent=1))


if __name__ == '__main__':
    main(sys.argv)