# greenplum-db-for-rocky
Development environment to start work on creating Greenplum Open
Source RPM for Rocky envioronments.

```
# Setup rpmbuild environment

sudo yum update
sudo yum check-update
sudo yum repolist all --enabled
sudo yum repolist all --disabled

adduser gpbuilder
sudo usermod -a -G wheel gpbuilder

sudo dnf install -y epel-release yum-utils git
sudo yum-config-manager --disable epel
sudo dnf install -y rpm-build wget curl rpmdevtools rpmlint
sudo dnf --enablerepo=epel install -d0 -y mock-core-configs
sudo usermod -a -G mock gpbuilder

# Generate diffs

git diff > gppylib-install.patch

# Copy dev files to rpmbuild systems

scp $HOME/workspace/rockylinux/greenplum-db-for-rocky/SPECS/greenplum.spec            rocky9:/home/eespino/workspace/greenplum-db-for-rocky/SPECS/greenplum.spec
scp $HOME/workspace/rockylinux/greenplum-db-for-rocky/SOURCES/gppylib-install.patch   rocky9:/home/eespino/workspace/rpmbuild/SOURCES/gppylib-install.patch
scp $HOME/workspace/rockylinux/greenplum-db-for-rocky/SOURCES/gp_bash_functions.patch rocky9:/home/eespino/workspace/rpmbuild/SOURCES/gp_bash_functions.patch

scp $HOME/workspace/rockylinux/greenplum-db-for-rocky/SPECS/greenplum.spec            rpmbuild8:/home/eespino/workspace/greenplum-db-for-rocky/SPECS/greenplum.spec
scp $HOME/workspace/rockylinux/greenplum-db-for-rocky/SOURCES/gppylib-install.patch   rpmbuild8:/home/eespino/workspace/rpmbuild/SOURCES/gppylib-install.patch
scp $HOME/workspace/rockylinux/greenplum-db-for-rocky/SOURCES/gp_bash_functions.patch rpmbuild8:/home/eespino/workspace/rpmbuild/SOURCES/gp_bash_functions.patch

# Setup rpmbuild environment

ssh rocky9

echo "%_topdir $HOME/workspace/rpmbuild" > $HOME/.rpmmacros
rpmdev-setuptree

# Clone Greenplum spec files

mkdir -p $HOME/workspace
cd $HOME/workspace
git clone https://github.com/edespino/greenplum-db-for-rocky.git

cd $HOME/workspace/rpmbuild
ln -s $HOME/workspace/greenplum-db-for-rocky/SPECS/greenplum.spec $HOME/workspace/rpmbuild/SPECS/greenplum.spec

# Retrieve Greenplum 7.0.0 Beta 2 source tarball

wget https://github.com/greenplum-db/gpdb/releases/download/7.0.0-beta.2/7.0.0-beta.2-src-full.tar.gz \
     -O $HOME/workspace/rpmbuild/SOURCES/7.0.0-beta.2-src-full.tar.gz

wget https://github.com/PyGreSQL/PyGreSQL/releases/download/5.2.4/PyGreSQL-5.2.4.tar.gz \
     -O $HOME/workspace/rpmbuild/SOURCES/PyGreSQL-5.2.4.tar.gz

# rpmbuild GPDB Rocky 8 Build Requirements

sudo dnf install -d0 -y apr-util-devel \
                        bison \
                        bzip2-devel \
                        clang-devel \
                        flex \
                        gcc \
                        gcc-c++ \
                        krb5-devel \
                        libcurl-devel \
                        libevent-devel \
                        libuuid-devel \
                        libxml2-devel \
                        libzstd-devel \
                        llvm-devel \
                        make \
                        openssl-devel \
                        pam-devel \
                        'perl(ExtUtils::Embed)' \
                        perl-devel \
                        python3-devel \
                        readline-devel \
                        zlib-devel

sudo dnf --enablerepo=powertools install -d0 -y libuv-devel libyaml-devel
sudo dnf --enablerepo=epel install -d0 -y xerces-c-devel

# Create Greenplum Source RPM package ($HOME/workspace/rpmbuild/SRPMS/greenplum-db-7.0.0-1.el8.src.rpm)
# from spec file ($HOME/workspace/rpmbuild/SPECS/greenplum.spec)

rm -rf $HOME/workspace/rpmbuild/BUILD/*
rpmlint $HOME/workspace/rpmbuild/SPECS/greenplum.spec
rpmbuild -bs \
         --define 'dist .el8' \
         --define "_topdir $HOME/workspace/rpmbuild" \
         $HOME/workspace/rpmbuild/SPECS/greenplum.spec

rpmbuild -ba \
         --define 'dist .el8' \
         --define "_topdir $HOME/workspace/rpmbuild" \
         $HOME/workspace/rpmbuild/SPECS/greenplum.spec

# Install GPDB  rpm

sudo yum erase -y greenplum-db
sudo yum install -y /home/eespino/workspace/rpmbuild/RPMS/x86_64/greenplum-db-7.0.0-1.el8.x86_64.rpm

# Perform RPM build using mock (https://github.com/rpm-software-management/mock)

mock --verbose \
     --root $HOME/workspace/greenplum-db-for-rocky/mock/rocky8-x86_64.cfg \
     --resultdir $HOME/workspace/rpmbuild/BUILD \
     --isolation simple \
     $HOME/workspace/rpmbuild/SRPMS/greenplum-db-7.0.0-1.el8.src.rpm

# Copy Greenplum binary rpm to Rocky 8 system
scp $HOME/workspace/rpmbuild/BUILD/greenplum-db-7.0.0-1.el8_GPDev.x86_64.rpm rocky8:

# Intialize a GPDB cluster

ssh rocky8

sudo dnf install -y greenplum-db-7.0.0-1.el8_GPDev.x86_64.rpm
sudo dnf --enablerepo=epel install -y greenplum-db-7.0.0-1.el8_GPDev.x86_64.rpm

sudo mkdir -p /data/coordinator /data/primary; sudo chown gpadmin.gpadmin /data/coordinator /data/primary

sudo usermod -a -G wheel gpadmin

sudo su - gpadmin

source /usr/greenplum_path.sh
echo $(hostname) > $HOME/hosts

cp /usr/docs/cli_help/gpconfigs/gpinitsystem_config .

# Update gpinitystem file.
sed -i -e "s|\(^declare -a DATA_DIRECTORY.*\)|declare -a DATA_DIRECTORY=(/data/primary)|" \
       -e "s|\(^#DATABASE_NAME=name_of_database.*$\)|DATABASE_NAME=gpadmin|" \
       -e "s|\(^COORDINATOR_HOSTNAME=.*$\)|COORDINATOR_HOSTNAME=$(hostname)|" $HOME/gpinitsystem_config

ssh-keygen -t rsa -b 4096 -C gpadmin -f $HOME/.ssh/id_rsa -P ""
cat $HOME/.ssh/id_rsa.pub >> $HOME/.ssh/authorized_keys
chmod 600 $HOME/.ssh/*
ssh rocky8 uptime
gpinitsystem -c gpinitsystem_config -h hosts -a

export COORDINATOR_DATA_DIRECTORY=/data/coordinator/gpseg-1

gpstop -a
gpstart -a
gpstate

psql postgres -c 'select version()'
psql postgres -c 'show optimizer'
psql postgres -c 'select * from gp_segment_configuration'
```
