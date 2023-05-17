## -------------------------------------------------------------------
## This is the Greenplum Database RPM spec file.
## This spec file and ancillary files are licensed in accordance with
## The Apache 2 License.
## -------------------------------------------------------------------

%{!?debug:%global debug 1}
%{!?debugextensions:%global debugextensions 1}
%{!?gpcloud:%global gpcloud 1}
%{!?gpfdist:%global gpfdist 1}
%{!?icproxy:%global icproxy 1}
%{!?kerberos:%global kerberos 1}
%{!?ldap:%global ldap 1}
%{!?libbz2:%global libbz2 1}
%{!?libcurl:%global libcurl 1}
%{!?libxml:%global libxml 1}
%{!?llvmjit:%global llvmjit 0}
%{!?mapreduce:%global mapreduce 1}
%{!?orafce:%global orafce 1}
%{!?orca:%global orca 1}
%{!?pam:%global pam 1}
%{!?plperl:%global plperl 1}
%{!?plpython3:%global plpython3 1}
%{!?ssl:%global ssl 1}
%{!?uuid:%global uuid 1}
%{!?zlib:%global zlib 1}
%{!?zstd:%global zstd 1}

# no debug infos with:
%global debug_package %{nil}

%global betamajorversion -beta.3

%global pygresqlversion 5.2.4

## -------------------------------------------------------------------

Summary: Greenplum Database Server
Name: greenplum-db
%global majorversion 7.0.0
Version: %{majorversion}
Release: 1%{?dist}

## -------------------------------------------------------------------

License: Apache 2
Url: https://github.com/greenplum-db/gpdb

## -------------------------------------------------------------------


Source0: https://github.com/greenplum-db/gpdb/releases/download/%{version}%{betamajorversion}/%{version}%{betamajorversion}-src-full.tar.gz
Source1: https://github.com/PyGreSQL/PyGreSQL/releases/download/%{pygresqlversion}/PyGreSQL-%{pygresqlversion}.tar.gz
Source2: gp.limits.conf
Patch1: gppylib-install.patch
Patch2: gp_bash_functions.patch
Patch3: mangling-shebang.patch

## -------------------------------------------------------------------

BuildRequires: make
BuildRequires: flex bison
BuildRequires: gcc
%if %orca
BuildRequires: gcc-c++ xerces-c-devel
%endif
%if %llvmjit
BuildRequires: llvm-devel >= 5.0 clang-devel >= 5.0
%endif
BuildRequires: readline-devel
%if %gpfdist
BuildRequires: apr-util-devel
BuildRequires: libevent-devel
BuildRequires: libyaml-devel
%endif
%if %uuid
BuildRequires: libuuid-devel
%endif
%if %ssl
BuildRequires: openssl-devel
%endif
%if %zlib
BuildRequires: zlib-devel
%endif
%if %gpcloud || %libxml
BuildRequires: libxml2-devel
%endif
%if %zstd
BuildRequires: libzstd-devel
%endif
%if %libbz2
BuildRequires: bzip2-devel
%endif
%if %libcurl
BuildRequires: libcurl-devel
%endif
%if %icproxy
BuildRequires: libuv-devel
%endif
%if %kerberos
BuildRequires: krb5-devel
%endif
%if %pam
BuildRequires: pam-devel
%endif

BuildRequires: perl(ExtUtils::Embed), perl-devel
BuildRequires: python3-devel

Requires: apr
Requires: bash
Requires: bzip2-libs
Requires: glibc
Requires: iproute
Requires: krb5-libs
Requires: less
Requires: libcgroup-tools
Requires: libcurl
Requires: libevent
Requires: libgcc
Requires: libstdc++
Requires: libuuid
Requires: libuv
Requires: libxml2
Requires: libyaml
Requires: libzstd
%if %llvmjit
Requires: llvm-libs
%endif
Requires: openldap
Requires: openssh
Requires: openssh-clients
Requires: openssh-server
Requires: openssl-libs
Requires: pam
Requires: perl
Requires: pkgconf-pkg-config
Requires: python3
Requires: python3-devel
Requires: python3-psutil
Requires: readline
Requires: rsync
Requires: sed
Requires: tar
Requires: which
Requires: xerces-c
Requires: zlib

Conflicts: postgresql
Conflicts: postgresql-contrib
Conflicts: postgresql-docs
Conflicts: postgresql-jdbc
Conflicts: postgresql-jdbc-javadoc
Conflicts: postgresql-odbc
Conflicts: postgresql-plperl
Conflicts: postgresql-plpython3
Conflicts: postgresql-pltcl
Conflicts: postgresql-server
Conflicts: postgresql-server-devel
Conflicts: postgresql-static
Conflicts: postgresql-test
Conflicts: postgresql-test-rpm-macros
Conflicts: postgresql-upgrade
Conflicts: postgresql-odbc-tests
Conflicts: postgresql-upgrade-devel

## -------------------------------------------------------------------

Group: Applications/Databases
%description
Greenplum Database (GPDB) is an advanced, fully featured, open source
data warehouse, based on PostgreSQL. It provides powerful and rapid
analytics on petabyte scale data volumes. Uniquely geared toward big
data analytics, Greenplum Database is powered by the world’s most
advanced cost-based query optimizer delivering high analytical query
performance on large data volumes.

## -------------------------------------------------------------------
## PREP section
## -------------------------------------------------------------------

%prep

%setup -q -b 1 -n PyGreSQL-%{pygresqlversion}
%setup -q -b 0 -n gpdb_src
%patch1 -p1
%patch2 -p1
%patch3 -p1

## -------------------------------------------------------------------
## BUILD section
## -------------------------------------------------------------------

%build

export PYTHON=%{python3}

common_configure_options='
                --disable-rpath
        %if %debug
                --enable-debug
                --enable-cassert
        %endif
        %if %zstd
                --with-zstd
        %else
                --without-zstd
        %endif
        %if %zlib
                --with-zlib
        %else
                --without-zlib
        %endif
        %if %gpfdist
                --enable-gpfdist
        %else
                --disable-gpfdist
        %endif
        %if %libcurl
                --with-libcurl
        %else
                --without-libcurl
        %endif
        %if %libbz2
                --with-libbz2
        %else
                --without-libbz2
        %endif
        %if %orca
                --enable-orca
        %else
                --disable-orca
        %endif
        %if %orafce
                --enable-orafce
        %else
                --disable-orafce
        %endif
        %if %gpcloud
                --enable-gpcloud
        %else
                --disable-gpcloud
        %endif
        %if %mapreduce
                --enable-mapreduce
        %else
                --disable-mapreduce
        %endif
        %if %libxml
                --with-libxml
        %else
                --without-libxml
        %endif
        %if %icproxy
                --enable-ic-proxy
        %else
                --disable-ic-proxy
        %endif
        %if %debugextensions
                --enable-debug-extensions
        %else
                --disable-debug-extensions
        %endif
        %if %plpython3
                --with-python
        %else
                --without-python
        %endif
        %if %ldap
                --with-ldap
        %else
                --without-ldap
        %endif
        %if %ssl
                --with-openssl
        %else
                --without-openssl
        %endif
        %if %kerberos
                --with-gssapi
        %else
                --without-gssapi
        %endif
        %if %pam
                --with-pam
        %else
                --without-pam
        %endif
        %if %plperl
                --with-perl
        %else
                --without-perl
        %endif
        %if %llvmjit
                --with-llvm
        %else
                --without-llvm
        %endif
        %if %uuid
                --with-uuid=e2fs
        %endif
'

## -------------------------------------------------------------------
## CONFIGURE section
## -------------------------------------------------------------------

%configure $common_configure_options

## -------------------------------------------------------------------
## MAKE_BUILD section
## -------------------------------------------------------------------

%make_build

## -------------------------------------------------------------------
## INSTALL section
## -------------------------------------------------------------------

%install

# Install GPDB
make install DESTDIR=$RPM_BUILD_ROOT

# Build and Install PyGreSQL
cd ..; cd PyGreSQL-%{pygresqlversion}

PATH=$RPM_BUILD_ROOT/usr/bin:$PATH \
%{python3} setup.py build

PATH=$RPM_BUILD_ROOT/usr/bin:$PATH \
%{python3} setup.py install --skip-build --root $RPM_BUILD_ROOT

find "$RPM_BUILD_ROOT/usr/lib64/python%{python3_version}/site-packages" \
     -type f \
     -name "*.so" | \
    while read so_file; do
        strip --strip-debug "$so_file"
    done

# Install /etc config file(s)
install -d $RPM_BUILD_ROOT/etc/security/limits.d
install -m 644 %{SOURCE2} $RPM_BUILD_ROOT/etc/security/limits.d

## -------------------------------------------------------------------
## PRE section
## -------------------------------------------------------------------

%pre
getent group gpadmin >/dev/null || /usr/sbin/groupadd \
        -r \
        gpadmin
getent passwd gpadmin >/dev/null || /usr/sbin/useradd \
        -r \
        -g gpadmin \
        -m \
        -d /var/lib/gpadmin \
        -s /bin/bash \
        -c "Greenplum Administrator account" gpadmin

## -------------------------------------------------------------------
## FILES section
## -------------------------------------------------------------------

%files

%defattr(-,gpadmin,gpadmin,-)
%{_prefix}/greenplum_path.sh
%{_bindir}/*
%{_prefix}/docs/cli_help
%{_includedir}/*
%{_prefix}/%{_lib}/lib*
%{_prefix}/%{_lib}/pkgconfig/*
%{_prefix}/%{_lib}/postgresql
%{python3_sitearch}/../gppylib
%{python3_sitearch}/PyGreSQL-%{pygresqlversion}-py%{python3_version}.egg-info
%{python3_sitearch}/__pycache__/pg.cpython-%{python3_version_nodots}.opt-1.pyc
%{python3_sitearch}/__pycache__/pg.cpython-%{python3_version_nodots}.pyc
%{python3_sitearch}/__pycache__/pgdb.cpython-%{python3_version_nodots}.opt-1.pyc
%{python3_sitearch}/__pycache__/pgdb.cpython-%{python3_version_nodots}.pyc
%{python3_sitearch}/_pg.cpython-%{python3_version_nodots}m-x86_64-linux-gnu.so
%{python3_sitearch}/pg.py
%{python3_sitearch}/pgdb.py
%{_libexecdir}/ifaddrs
%{_sbindir}/*
%{_docdir}/postgresql
%{_datadir}/greenplum
%{_datadir}/postgresql

%defattr(-,root,root,-)
%{_sysconfdir}/security/limits.d/gp.limits.conf

## -------------------------------------------------------------------
## CHANGELOGFILES section
## -------------------------------------------------------------------

%changelog
* Tue May 09 2023 Ed Espino <eespino@vmware.com> - 7.0.0-beta.3
- Greenplum 7.0.0 Beta 3 release.

* Tue Apr 25 2023 Ed Espino <eespino@vmware.com> - 7.0.0-beta.2
- Greenplum 7.0.0 Beta 2 release.
