import os
import collections

image_cache = {}
DEFAULT_IMG = "img_not_found"

def cache_image(name, image):
    """Stores the specified name-image pair in the cache dictionary.
    
    Args:
        name: The name for the new cache record.
        image: The image (PyGame Surface) to store.
    """
    image_cache[name] = image

    
def get_image(name): #TODO
    """Gets the specified cached image or returns the default image if there is
    no cache record with the given name.
    
    Args:
        name: The name of the cached image to retrieve.
    Returns:
        pygame.Surface: Cached image object.
    """
    if name in image_cache:
        return image_cache[name]
    elif DEFAULT_IMG in image_cache:
        return image_cache[DEFAULT_IMG]
    else:
        raise KeyError("The image << " + name + " >> is not in the cache and "
            "the fallback image cannot be found.")

            
def file_name(file_path):
    """Trims a file's path into just its name and returns it.
    
    Args:
        file_path: The file path to be manipulated.
    Returns:
        string: The file's name, without any directories or extensions.
    """
    try:
        return os.path.splitext(os.path.split(file_path)[1])[0]
    except:
        raise ValueError("utils.file_name() cannot parse <<" + file_path + ">>")

        
def get_filenames_r(dir, ext=None):
    """Return all files in a specific directory (including those in
    subdirectories).
    
    Args:
        dir: Directory to crawl for files.
        ext (optional): The file extension (as a string) or extensions (as a
            collection of strings)
    Returns:
        A list of all matching file paths in the given directory.
    See:
        http://stackoverflow.com/questions/19587118/python-iterating-through-directories
        http://stackoverflow.com/questions/1952464/in-python-how-do-i-determine-if-an-object-is-iterable
    """
    matches = []
    
    for sub, dirs, files in os.walk(dir):
        for file in files:
            file_ext = file.split('.')[-1]
            
            if ext is None:
                matches.append(os.path.join(sub, file))
            elif file_ext in ext:
                matches.append(os.path.join(sub, file))

    return matches


def ini_to_dict(f):
    """Creates a dictionary from the specified INI file.

    Args:
        file_name (str): The path to the desired INI file.
    Returns:
        dict: A dictionary populated with data from the INI file.
    Raises:
        TypeError, IOError
    """
    
    """NOTE: floats aren't supported for dynamic casting"""
    
    if type(f) is str:
        ini_file = open(f, 'r')
    elif not isinstance(f, file):
        raise TypeError("ini_to_dict() requires a file name (string) or file "
            "object as an argument.")
    
    root_dict = collections.OrderedDict()
    fill_dict = root_dict # current dict being filled by the parser
    
    for line in ini_file:
        line = line.strip()
        
        # Skip comments and empty lines
        if line.startswith(";") or not line:
            continue
            
        # Handle sections
        elif line.startswith("[") and line.endswith("]"):
            section_name = line[1:-1]
            
            # If the square brackets are empty or are named "root", resume
            # filling the root dictionary.
            if (section_name is None) or (section_name.lower() == "root"):
                fill_dict = root_dict
                continue
            
            # Create a section in the fill dict if one doesn't already exist
            if section_name not in root_dict:
                root_dict[section_name] = {}
            
            # Now start filling up this inner dict
            fill_dict = root_dict[section_name] # Start filling the inner dict now
        
        # Handle k/v pairs
        elif line.find("=") != -1:
            key, value = line.split("=")
            key = key.strip()
            value = value.strip()
            
            # Dynamic str -> int casting. Floats not supported in this impl!!
            if value.isdigit():
                value = int(value)
            
            fill_dict[key] = value
            
        # The INI file is probably malformed
        else:
            file_path = os.path.join(os.path.abspath(ini_file.name))
            raise IOError("The specified INI file << " + file_path + " >> is "
                "not formed properly.")
        
    ini_file.close()
    
    return root_dict