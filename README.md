# greenplum-db-for-rocky
Development environment to start work on creating Greenplum Open
Source RPM for Rocky envioronments.

```
# Setup rpmbuild environment
# Provision a minimal rocky 9 system

sudo yum update
sudo yum check-update

# View repo list
sudo yum repolist all --enabled
sudo yum repolist all --disabled

# Add Greenplum builder account
adduser gpbuilder
sudo usermod -a -G wheel gpbuilder

# Add supporting rpmbuild tools
sudo dnf install -y epel-release yum-utils git
sudo yum-config-manager --disable epel
sudo dnf install -y rpm-build wget curl rpmdevtools rpmlint
sudo dnf --enablerepo=epel install -d0 -y mock-core-configs
sudo usermod -a -G mock gpbuilder

# Generate patch file example
git diff > gppylib-install.patch

# Copy dev files to rpmbuild systems
# Example commands

# rocky 9 - rpmbuild mock environment
scp $HOME/workspace/rockylinux/greenplum-db-for-rocky/SPECS/greenplum.spec            rocky9:workspace/greenplum-db-for-rocky/SPECS/greenplum.spec
scp $HOME/workspace/rockylinux/greenplum-db-for-rocky/SOURCES/gp.limits.conf          rocky9:workspace/rpmbuild/SOURCES/gp.limits.conf
scp $HOME/workspace/rockylinux/greenplum-db-for-rocky/SOURCES/gppylib-install.patch   rocky9:workspace/rpmbuild/SOURCES/gppylib-install.patch
scp $HOME/workspace/rockylinux/greenplum-db-for-rocky/SOURCES/gp_bash_functions.patch rocky9:workspace/rpmbuild/SOURCES/gp_bash_functions.patch

# rocky 8 - rpmbuild non-mock environment
scp $HOME/workspace/rockylinux/greenplum-db-for-rocky/SOURCES/gp.limits.conf          rpmbuild8:workspace/rpmbuild/SOURCES/gp.limits.conf
scp $HOME/workspace/rockylinux/greenplum-db-for-rocky/SPECS/greenplum.spec            rpmbuild8:workspace/greenplum-db-for-rocky/SPECS/greenplum.spec
scp $HOME/workspace/rockylinux/greenplum-db-for-rocky/SOURCES/gppylib-install.patch   rpmbuild8:workspace/rpmbuild/SOURCES/gppylib-install.patch
scp $HOME/workspace/rockylinux/greenplum-db-for-rocky/SOURCES/gp_bash_functions.patch rpmbuild8:workspace/rpmbuild/SOURCES/gp_bash_functions.patch

# Setup rpmbuild environment
ssh rocky9

echo "%_topdir $HOME/workspace/rpmbuild" > $HOME/.rpmmacros
rpmdev-setuptree

# Clone Greenplum spec files

cd $HOME/workspace
git clone https://github.com/edespino/greenplum-db-for-rocky.git

cd $HOME/workspace/rpmbuild
ln -s $HOME/workspace/greenplum-db-for-rocky/greenplum.spec $HOME/workspace/rpmbuild/SPECS/greenplum.spec

# Retrieve Greenplum 7.0.0 Beta 2 source tarball

wget https://github.com/greenplum-db/gpdb/releases/download/7.0.0-beta.3/7.0.0-beta.3-src-full.tar.gz \
     -O $HOME/workspace/rpmbuild/SOURCES/7.0.0-beta.3-src-full.tar.gz

wget https://github.com/PyGreSQL/PyGreSQL/releases/download/5.2.4/PyGreSQL-5.2.4.tar.gz \
     -O $HOME/workspace/rpmbuild/SOURCES/PyGreSQL-5.2.4.tar.gz

cp -v $HOME/workspace/greenplum-db-for-rocky/*.patch $HOME/workspace/greenplum-db-for-rocky/*.gz $HOME/workspace/rpmbuild/SOURCES

# Cleanup
rm -rf $HOME/workspace/rpmbuild/BUILD/*

# Run rpmlint against spec file
rpmlint $HOME/workspace/rpmbuild/SPECS/greenplum.spec

# Create Greenplum Source RPM package ($HOME/workspace/rpmbuild/SRPMS/greenplum-db-7.0.0-1.el8.src.rpm)
# from spec file ($HOME/workspace/rpmbuild/SPECS/greenplum.spec)

rpmbuild -bs \
         --define 'dist .el8' \
         --define "_topdir $HOME/workspace/rpmbuild" \
         $HOME/workspace/rpmbuild/SPECS/greenplum.spec

mock --verbose \
     --root $HOME/workspace/greenplum-db-for-rocky/mock/rocky8-x86_64.cfg \
     --resultdir $HOME/workspace/rpmbuild/BUILD \
     --isolation simple \
     $HOME/workspace/rpmbuild/SRPMS/greenplum-db-7.0.0-1.el8.src.rpm

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

# Copy Greenplum binary rpm to Rocky 8 system
scp $HOME/workspace/rpmbuild/BUILD/greenplum-db-7.0.0-1.el8_GPDev.x86_64.rpm rocky8:

# Intialize a GPDB cluster

ssh rocky8

sudo dnf install -y greenplum-db-7.0.0-1.el8_GPDev.x86_64.rpm
sudo dnf --enablerepo=epel install -y greenplum-db-7.0.0-1.el8_GPDev.x86_64.rpm
sudo dnf --enablerepo=epel install -y postgresql

sudo mkdir -p /data/coordinator /data/{primary,mirror}; sudo chown gpadmin.gpadmin /data/coordinator /data/{primary,mirror}

sudo usermod -a -G wheel gpadmin

sudo su - gpadmin

source /usr/greenplum_path.sh
echo $(hostname) > $HOME/hosts

cp /usr/docs/cli_help/gpconfigs/gpinitsystem_config .

# Update gpinitystem file.
sed -i -e "s|\(^declare -a DATA_DIRECTORY.*\)|declare -a DATA_DIRECTORY=(/data/primary)|" \
       -e "s|\(^#declare -a MIRROR_DATA_DIRECTORY.*\)|declare -a MIRROR_DATA_DIRECTORY=(/data/mirror)|" \
       -e "s|^#MIRROR_PORT_BASE=7000|MIRROR_PORT_BASE=7000|" \
       -e "s|\(^#DATABASE_NAME=name_of_database.*$\)|DATABASE_NAME=gpadmin|" \
       -e "s|\(^COORDINATOR_HOSTNAME=.*$\)|COORDINATOR_HOSTNAME=$(hostname)|" $HOME/gpinitsystem_config

ssh-keygen -t rsa -b 4096 -C gpadmin -f $HOME/.ssh/id_rsa -P ""
cat $HOME/.ssh/id_rsa.pub >> $HOME/.ssh/authorized_keys
chmod 600 $HOME/.ssh/*
ssh -o StrictHostKeyChecking=no rocky8 uptime
gpinitsystem -c gpinitsystem_config -h hosts -a

# Basic deployment validation commands.
export COORDINATOR_DATA_DIRECTORY=/data/coordinator/gpseg-1

psql postgres -c 'select version()'
psql postgres -c 'show optimizer'
psql postgres -c 'select * from gp_segment_configuration'

gpstate -s
gpstate -Q
gpstate -m
gpstate -f
gpstate -x
gpstate -i
gpstate -e
gpstop -a
gpstart -a

sudo dnf --enablerepo=epel install -d0 tito
sudo usermod -a -G mock gpbuilder

```




gcc -Wall -Wmissing-prototypes -Wpointer-arith -Werror=vla -Wendif-labels -Wmissing-format-attribute -Wformat-security -fno-strict-aliasing -fwrapv -fexcess-precision=standard -Wno-unused-but-set-variable -Werror=implicit-fallthrough=3 -Wno-format-truncation -Wno-stringop-truncation -g -O2 -g -pipe -Wall -Werror=format-security -Wp,-D_FORTIFY_SOURCE=2 -Wp,-D_GLIBCXX_ASSERTIONS -fexceptions -fstack-protector-strong -grecord-gcc-switches -specs=/usr/lib/rpm/redhat/redhat-hardened-cc1 -specs=/usr/lib/rpm/redhat/redhat-annobin-cc1 -m64 -mtune=generic -fasynchronous-unwind-tables -fstack-clash-protection -fcf-protection  -Werror=uninitialized -Werror=implicit-function-declaration  -Wno-deprecated-declarations -fPIC -D__STDC_LIMIT_MACROS -D__STDC_FORMAT_MACROS -D__STDC_CONSTANT_MACROS -D_GNU_SOURCE -I/usr/include  -I../../../../src/include   -D_GNU_SOURCE -I/usr/include/libxml2   -c -o llvmjit.o llvmjit.c

gcc -Wall -Wmissing-prototypes -Wpointer-arith -Werror=vla -Wendif-labels -Wmissing-format-attribute -Wformat-security -fno-strict-aliasing -fwrapv -fexcess-precision=standard -Wno-unused-but-set-variable -Werror=implicit-fallthrough=3 -Wno-format-truncation -Wno-stringop-truncation -g -O2 -g -pipe -Wall -Werror=format-security -Wp,-D_FORTIFY_SOURCE=2 -Wp,-D_GLIBCXX_ASSERTIONS -fexceptions -fstack-protector-strong -grecord-gcc-switches -specs=/usr/lib/rpm/redhat/redhat-hardened-cc1 -specs=/usr/lib/rpm/redhat/redhat-annobin-cc1 -m64 -mtune=generic -fasynchronous-unwind-tables -fstack-clash-protection -fcf-protection  -Werror=uninitialized -Werror=implicit-function-declaration  -Wno-deprecated-declarations -fPIC -D__STDC_LIMIT_MACROS -D__STDC_FORMAT_MACROS -D__STDC_CONSTANT_MACROS -D_GNU_SOURCE -I/usr/include  -I../../../../src/include   -D_GNU_SOURCE -I/usr/include/libxml2   -c -o llvmjit.o llvmjit.c
gcc -Wall -Wmissing-prototypes -Wpointer-arith -Werror=vla -Wendif-labels -Wmissing-format-attribute -Wformat-security -fno-strict-aliasing -fwrapv -fexcess-precision=standard -Wno-unused-but-set-variable -Werror=implicit-fallthrough=3 -Wno-format-truncation -Wno-stringop-truncation -g -O2 -g -pipe -Wall -Werror=format-security -Wp,-D_FORTIFY_SOURCE=2 -Wp,-D_GLIBCXX_ASSERTIONS -fexceptions -fstack-protector-strong -grecord-gcc-switches -specs=/usr/lib/rpm/redhat/redhat-hardened-cc1 -specs=/usr/lib/rpm/redhat/redhat-annobin-cc1 -m64 -mtune=generic -fasynchronous-unwind-tables -fstack-clash-protection -fcf-protection  -Werror=uninitialized -Werror=implicit-function-declaration  -Wno-deprecated-declarations -fPIC -D__STDC_LIMIT_MACROS -D__STDC_FORMAT_MACROS -D__STDC_CONSTANT_MACROS -D_GNU_SOURCE -I/usr/include  -I../../../../src/include   -D_GNU_SOURCE -I/usr/include/libxml2   -c -o llvmjit.o llvmjit.c

+ CFLAGS='-O2 -g -pipe -Wall -Werror=format-security -Wp,-D_FORTIFY_SOURCE=2 -Wp,-D_GLIBCXX_ASSERTIONS -fexceptions -fstack-protector-strong -grecord-gcc-switches -specs=/usr/lib/rpm/redhat/redhat-hardened-cc1 -specs=/usr/lib/rpm/redhat/redhat-annobin-cc1 -m64 -mtune=generic -fasynchronous-unwind-tables -fstack-clash-protection -fcf-protection'
+ CFLAGS='-O2 -g -pipe -Wall -Werror=format-security -Wp,-D_FORTIFY_SOURCE=2 -Wp,-D_GLIBCXX_ASSERTIONS -fexceptions -fstack-protector-strong -grecord-gcc-switches -specs=/usr/lib/rpm/redhat/redhat-hardened-cc1 -specs=/usr/lib/rpm/redhat/redhat-annobin-cc1 -m64 -mtune=generic -fasynchronous-unwind-tables -fstack-clash-protection -fcf-protection'
