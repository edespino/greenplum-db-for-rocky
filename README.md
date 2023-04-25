# greenplum-db-for-rocky
Development environment to start work on creating Greenplum Open
Source RPM for Rocky envioronments.

```
# Setup rpmbuild environment
echo "%_topdir $HOME/workspace/rpmbuild" > $HOME/.rpmmacros
rpmdev-setuptree

# Clone Greenplum spec files
cd $HOME/workspace
git clone https://github.com/edespino/greenplum-db-for-rocky.git

cd $HOME/workspace/rpmbuild
ln -s $HOME/workspace/greenplum-db-for-rocky/SPECS/greenplum.spec $HOME/workspace/rpmbuild/SPECS/greenplum.spec

# Retrieve Greenplum 7.0.0 Beta 2 source tarball
wget https://github.com/greenplum-db/gpdb/releases/download/7.0.0-beta.2/7.0.0-beta.2-src-full.tar.gz \
     -O $HOME/workspace/rpmbuild/SOURCES/7.0.0-beta.2-src-full.tar.gz

# Create Greenplum Source RPM package ($HOME/workspace/rpmbuild/SRPMS/greenplum-db-7.0.0-1.el8.src.rpm)
# from spec file ($HOME/workspace/rpmbuild/SPECS/greenplum.spec)
rm -rf $HOME/workspace/rpmbuild/BUILD/*
rpmlint $HOME/workspace/rpmbuild/SPECS/greenplum.spec
rpmbuild -bs \
         --define 'dist .el8' \
         --define "_topdir $HOME/workspace/rpmbuild" \
         $HOME/workspace/rpmbuild/SPECS/greenplum.spec

# Perform RPM build using mock (https://github.com/rpm-software-management/mock)
mock --verbose \
     --root $HOME/workspace/greenplum-db-for-rocky/mock/rocky8-x86_64.cfg \
     --resultdir $HOME/workspace/rpmbuild/BUILD \
     --isolation simple \
     $HOME/workspace/rpmbuild/SRPMS/greenplum-db-7.0.0-1.el8.src.rpm

# Copy Greenplum binary rpm to Rocky 8 system
scp $HOME/workspace/rpmbuild/BUILD/greenplum-db-7.0.0-1.el8_GPDev.x86_64.rpm rocky8:

# Perform installation on Rocky 8 environment

sudo yum install -y ~eespino/greenplum-db-7.0.0-1.el8_GPDev.x86_64.rpm
sudo pip3 install psutil pygresql

source /usr/greenplum_path.sh
export PYTHONPATH=/usr/lib64/python:$PYTHONPATH

```
