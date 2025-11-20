##
# Copyright 2023 Maxime Boissonneault
#
# This file is triple-licensed under GPLv2 (see below), MIT, and
# BSD three-clause licenses.
#
# This file is part of EasyBuild,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://www.vscentrum.be),
# Flemish Research Foundation (FWO) (http://www.fwo.be/en)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# http://github.com/hpcugent/easybuild
#
# EasyBuild is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
#
# EasyBuild is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with EasyBuild.  If not, see <http://www.gnu.org/licenses/>.
##
"""
General EasyBuild support for software, using containerized applications
Based on https://gitrepo.service.rug.nl/cit-hpc/habrok/cit-hpc-easybuild/-/blob/main/easyblocks/generic/apptainer.py

@author: Maxime Boissonneault (Universite Laval, Calcul Quebec, Digital Research Alliance of Canada)
@author: Aurel Istrate (c.a.istrate@rug.nl)
"""
import os
import re
from easybuild.easyblocks.generic.binary import Binary
from easybuild.framework.easyconfig import CUSTOM
from easybuild.tools.build_log import EasyBuildError

DEFAULT_INSTALL_CMD = "build_container_image.sh "
class Apptainer(Binary):
    """
    Support for installing software via an Apptainer container
    """

    @staticmethod
    def extra_options(extra_vars=None):
        """Extra easyconfig parameters specific to Binary easyblock."""
        extra_vars = Binary.extra_options(extra_vars)
        extra_vars.update({
            'aliases': [[], "Commands to alias in the module.", CUSTOM],
            'apptainer_params': ["", "Default parameters for apptainer", CUSTOM],
            'apptainer_type': ["", "Type of apptainer installation (sandbox or sif)", CUSTOM],
        })
        return extra_vars

    def __init__(self, *args, **kwargs):
        """Initialize custom class variables."""
        super(Apptainer, self).__init__(*args, **kwargs)

        # do not prepend anything to path like binary does
        self.cfg['prepend_to_path'] = None

    def extract_step(self):
        """No extract step"""
        if self.src:
            super(Apptainer, self).extract_step()

    def install_step(self):
        # Set the installation command
        apptainer_type = self.cfg['apptainer_type']
        
        self.cfg['install_cmd'] = DEFAULT_INSTALL_CMD + '-t ' + apptainer_type + ' '
        self.cfg['install_cmd'] += '-n ' + self.name.lower() + ' -v ' + self.version + ' '
        self.cfg['install_cmd'] += "-o " + self.installdir + ' '

        super(Apptainer, self).install_step()

    def make_module_req(self):
        """
        Don't extend PATH/LIBRARY_PATH/etc.
        """
        return ""

    def make_module_extra(self, *args, **kwargs):   
        """Overwritten from Application to add extra txt"""
        
        apptainer_type = self.cfg['apptainer_type']
        container_path = self.installdir + '/' 
        
        # Set container_path based on type
        if apptainer_type == 'sif':
            container_image = container_path + self.name.lower() + '-' + self.version + '.sif'
        else:  # sandbox
            container_image = '-c ' + container_path

        txt = super(Apptainer, self).make_module_extra(*args, **kwargs)
        for alias in self.cfg["aliases"]:
            txt += self.module_generator.set_alias(alias, "apptainer exec %s %s %s" % (self.cfg['apptainer_params'], container_image, alias))
        return txt

    def sanity_check_step(self):
        """
        Custom sanity check step for Apptainer: check that aliases run
        """

        apptainer_type = self.cfg['apptainer_type']
        # For module file generation: temporarly set installdir to container path for sandbox
        if apptainer_type == 'sandbox':
            orig_installdir = self.installdir
            self.installdir += '/' + self.name.lower() + '-' + self.version

            # sanity check
            res = super(Apptainer, self).sanity_check_step()

            # Reset installdir to EasyBuild values
            self.installdir = orig_installdir
        else: # sif file
            res = super(Apptainer, self).sanity_check_step()

        return res
