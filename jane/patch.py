
def _patch_bytes(data,replacements):
    original_size = len(data)
    data_lower = data.lower()
    for replace_p, replace_with_p in replacements:
        patched = []
        if not replace_p:
            break
        if callable(replace_p):
            replace_p = replace_p(data)
        if callable(replace_with_p):
            replace_with_p = replace_with_p(data)

        replace = replace_p.encode()
        replace_with = replace_with_p.encode()
        replace_lower = replace.lower()
        data = data.replace(replace,replace_with)
        continue
        print(replace,replace_with)
        previous_index = 0
        while True:
            found_index = data_lower[previous_index:].find(replace_lower)
            while found_index == previous_index:
                previous_index+=1
                found_index = data_lower[previous_index:].find(replace_lower)
                if found_index == -1:
                    break
                #found_index += previous_index + 1
                #break 
                print("patched ",found_index,previous_index)

            if found_index == -1:
                print(found_index)
                break
            previous_index = found_index + len(replace)
            to_replace = data[found_index:found_index+len(replace)]
            #patched.append(found_index)
            data = data.replace(to_replace, replace_with)
            data_old = data.lower()
            data_lower = data.lower()
            if data_old == data_lower:
                break
    return data

async def patch_bytes(*args,**kwargs):
    return _patch_bytes(*args,**kwargs)
