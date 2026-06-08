import os, json
from cffi import FFI
import numpy as np

ffi = FFI()
ffi.cdef('int cal(const char* json_str, unsigned char* out_buffer);')

_current_dir = os.path.dirname(os.path.abspath(__file__))
_lib_path = os.path.join(_current_dir, 'lib', 'cgh_engine.dylib')

lib = ffi.dlopen(_lib_path)



def _serialize_mode(mode):
    if not mode.is_leaf:
        plus, minus = mode.flatten()
        return {
            'type': 'PM',
            'children': {
                'plus': [_serialize_mode(m) for m in plus],
                'minus': [_serialize_mode(m) for m in minus],
            }
        }

    elif mode.is_leaf:
        return {
            'type': mode.__class__.__name__,
            'o1': mode.order_1,
            'o2': mode.order_2,
            'sx': float(mode.x_shift),
            'sy': float(mode.y_shift),
        }



def _serialize_cgh(cgh):
    data = {
        'global': {
            'sigma': float(cgh.sigma),
            'pixel_size': float(cgh.slm_cls.pixel_size),
            'resolution': list(cgh.slm_cls.resolution),
        },
        'modes': []
    }

    for mode, nx, ny in zip(cgh.mode_list, cgh.nx_list, cgh.ny_list):

        mode_json = _serialize_mode(mode)

        mode_json['nx'] = float(nx)
        mode_json['ny'] = float(ny)

        data['modes'].append(mode_json)

    return data



def cal_cpp(cgh_instance):
    ir_dict = _serialize_cgh(cgh_instance)
    json_bytes = json.dumps(ir_dict).encode('utf-8')

    res_x, res_y = ir_dict['global']['resolution']
    cgh_array = np.zeros((res_y, res_x), dtype=np.uint8)
    out_ptr = ffi.cast('unsigned char*', ffi.from_buffer(cgh_array))

    status = lib.cal(json_bytes, out_ptr)
    if status != 0:
        raise RuntimeError

    return cgh_array