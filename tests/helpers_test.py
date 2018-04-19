import os
import io

import pytest

from tests.fixtures import dir_fixture, func_dir_fixture

from webdriver_manager import helpers


class Test_normalize_outputdir:

    def test_normalize_outputdir_no_params(self, dir_fixture):
        os.chdir(dir_fixture['path'])
        outputdir = helpers.normalize_outputdir()
        assert outputdir == dir_fixture['path']

    def test_normalize_outputdir_None(self, dir_fixture):
        os.chdir(dir_fixture['path'])
        outputdir = helpers.normalize_outputdir(None)
        assert outputdir == dir_fixture['path']

    def test_normalize_outputdir_None_drivers_path_exists(self, func_dir_fixture):
        os.chdir(func_dir_fixture['path'])
        drivers_path = os.path.join(func_dir_fixture['path'], 'drivers')
        os.makedirs(drivers_path)
        outputdir = helpers.normalize_outputdir(None)
        assert outputdir == drivers_path    

    def test_normalize_outputdir_no_slashes(self, dir_fixture):
        os.chdir(dir_fixture['path'])
        outputdir = helpers.normalize_outputdir('example')
        expected = os.path.join(dir_fixture['path'], 'example')
        assert outputdir == expected

    def test_normalize_outputdir_beginning_slash(self, dir_fixture):
        os.chdir(dir_fixture['path'])
        outputdir = helpers.normalize_outputdir('/example')
        expected = os.path.abspath('/example')
        assert outputdir == expected

    @pytest.mark.skipif('helpers.get_platform()["os_name"] != "windows"')
    def test_normalize_outputdir_beginning_backslash(self, dir_fixture):
        os.chdir(dir_fixture['path'])
        outputdir = helpers.normalize_outputdir('\example')
        expected = os.path.abspath('\example')
        assert outputdir == expected

    @pytest.mark.skipif('helpers.get_platform()["os_name"] != "windows"')
    def test_normalize_outputdir_beginning_dot_slash(self, dir_fixture):
        os.chdir(dir_fixture['path'])
        outputdir = helpers.normalize_outputdir('./example')
        expected = os.path.join(dir_fixture['path'], 'example')
        assert outputdir == expected

    def test_normalize_outputdir_beginning_dot_backslash(self, dir_fixture):
        os.chdir(dir_fixture['path'])
        outputdir = helpers.normalize_outputdir('.\example')
        expected = os.path.join(dir_fixture['path'], 'example')
        assert outputdir == expected

    def test_normalize_outputdir_absolute_path(self, dir_fixture):
        os.chdir(dir_fixture['path'])
        absolute_path = os.path.join(dir_fixture['path'], 'drivers')
        outputdir = helpers.normalize_outputdir(absolute_path)
        assert outputdir == absolute_path

    @pytest.mark.skipif('helpers.get_platform()["os_name"] != "windows"')
    def test_normalize_outputdir_absolute_path_windows(self, dir_fixture):
        os.chdir(dir_fixture['path'])
        absolute_path = 'C:\\absolute\\path'
        outputdir = helpers.normalize_outputdir(absolute_path)
        assert outputdir == absolute_path

    @pytest.mark.skipif('helpers.get_platform()["os_name"] != "windows"')
    def test_normalize_outputdir_absolute_path_windows_end_backlash(self, dir_fixture):
        os.chdir(dir_fixture['path'])
        absolute_path = 'C:\\absolute\\path\\'
        expected = 'C:\\absolute\\path'
        outputdir = helpers.normalize_outputdir(absolute_path)
        assert outputdir == expected

    def test_normalize_outputdir_backslash_escaped_char(self, dir_fixture):
        os.chdir(dir_fixture['path'])
        outputdir = helpers.normalize_outputdir('\\bbb')
        expected = os.path.abspath('\\bbb')
        assert outputdir == expected

    @pytest.mark.skipif('helpers.get_platform()["os_name"] != "windows"')
    def test_normalize_outputdir_dot_backslash_escaped_char(self, dir_fixture):
        os.chdir(dir_fixture['path'])
        outputdir = helpers.normalize_outputdir('.\\b\\n\\t')
        expected = os.path.join(dir_fixture['path'], 'b', 'n', 't')
        assert outputdir == expected


class Test_get_driver_class:

    def test_get_driver_class_chrome(self):
        cls = helpers.get_driver_class('chrome')
        assert repr(cls) == "<class 'webdriver_manager.webdriver.chromedriver.Chromedriver'>"
        
    def test_get_driver_class_firefox(self):
        cls = helpers.get_driver_class('firefox')
        assert repr(cls) == "<class 'webdriver_manager.webdriver.geckodriver.Geckodriver'>"

    def test_get_driver_class_incorrect_driver_name(self):
        with pytest.raises(Exception) as excinfo:
            cls = helpers.get_driver_class('incorrect_driver')
        assert str(excinfo.value) == 'driver incorrect_driver is not implemented'


class Test_split_driver_name_and_version:

    def test_split_driver_name_and_version_no_version(self):
        driver_name, req_version = helpers.split_driver_name_and_version('test')
        assert driver_name == 'test'
        assert req_version == None

    def test_split_driver_name_and_version_with_valid_version(self):
        driver_name, req_version = helpers.split_driver_name_and_version('test=3.3.3')
        assert driver_name == 'test'
        assert req_version == '3.3.3'


class Test_download_file_with_progress_bar:

    @pytest.mark.slow
    def test_download_file_with_progress_bar_download_jquery(self):
        url = 'https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js'
        result = helpers.download_file_with_progress_bar(url)
        assert isinstance(result, io._io.BytesIO)

    def test_download_file_with_progress_bar_400_error(self, caplog):
        url = 'https://ajax.googleapis.com/ajax/libs/jquery/9.9.9/jquery.min.js'
        with pytest.raises(SystemExit):
            result = helpers.download_file_with_progress_bar(url)
        assert caplog.records[0].levelname == 'ERROR'
        msg = ('there was a 404 error trying to reach {} \nThis probably '
               'means the requested version does not exist.'.format(url))
        assert caplog.records[0].message == msg


class Test_driver_to_executable_filename:

    def test_driver_to_executable_filename(self):
        result = helpers.browser_to_driver_name('chrome')
        assert result == 'chromedriver'

    def test_driver_to_executable_filename(self):
        result = helpers.browser_to_driver_name('firefox')
        assert result == 'geckodriver'

    def test_driver_to_executable_filename(self):
        with pytest.raises(Exception) as excinfo:
            cls = helpers.get_driver_class('incorrect_driver')
        assert str(excinfo.value) == 'driver incorrect_driver is not implemented'