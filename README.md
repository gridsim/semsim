Table of Contents
===

 1. Synopsis
 2. Latest Version
 3. Installation
 4. Run
 5. Documentation
 6. Bug Reporting
 7. Contributors
 8. Contacts
 9. License
 10. Copyright


1. Synopsis
===
SemSim is a building simulator developed for the SEMIAH (http://semiah.eu) 
european project. 


2. Latest Version
===
You can find the latest version of SemSim on :
    https://github.com/gridsim/


3. Installation
===
SemSim is a full python project thus as long as Python is installed on your
system you can install it by moving in the root folder (the folder this README
file should be) and run :

    python setup.py install

Warning : SemSim requires these packages to be used in full :

 * gridsim
 * influxdb
 
4. Run
===
SemSim is an executable project thus you can run it by moving in the root 
folder (the folder this README file should be) and run :

    python semsim/main.py <jsonfile>

with, `<jsonfile>` a json file representing the simulation.

Warning : SemSim requires these packages to be used in full :

 * gridsim
 * influxdb


5. Documentation
===
A documentation is provided with this release in './doc' folder.


6. Bug Reporting
===
If you find any bugs, or if you want new features you can put your request on
github at the following address :
    https://github.com/gridsim/semsim


7. Contributors
===

The SemSim Team is currently composed of :

 * Dominique Gabioud (dominique.gabioud@hevs.ch)
 * Gillian Basso (gillian.basso@hevs.ch)
 * Pierre Ferrez (pierre.ferrez@hevs.ch)
 * Pierre Roduit (pierre.roduit@hevs.ch)


8. Contacts
===
For questions, bug reports, patches and new elements / modules, contact :
gridsim@hevs.ch.


9. License
===
You should have received a copy of the GNU General Public License along with
this program.
If not, see <http://www.gnu.org/licenses/>.


10. Copyright
===
Copyright (C) 2011-2015 The Gridsim Team

This file is part of the Gridsim project.

The SemSim project is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the Free
Software Foundation; either version 3 of the License, or (at your option) any
later version.

The SemSim project is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.
