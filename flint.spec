%global with_snapshot 1

%if %{with_snapshot}
%global commit 4b383e23b39099f5ba09f7758023440e76277fc1
%global shortcommit %(c=%{commit}; echo ${c:0:7})
# date +%Y%m%d
%global date 20130801
%global snapshot .%{date}git%{shortcommit}
%else
%global snapshot %{nil}
%endif

Name:           flint
Version:        2.3
Release:        1%{snapshot}%{?dist}
Summary:        Fast Library for Number Theory
License:        GPLv2+
URL:            http://www.flintlib.org/
%if %{with_snapshot}
Source0:        https://github.com/wbhart/flint2/archive/%{commit}/%{name}-%{version}-%{shortcommit}.tar.gz
%else
Source0:        http://www.flintlib.org/flint-%{version}.tar.gz
%endif
Source1:        %{name}.rpmlintrc

# Minor changes to configure and Makefile.in for proper use of ${_lib}
# and generation of a shared library with a soname
Patch0:         %{name}-rpmbuild.patch

# Workaround bug in the create_doc build program that triggers an error
# for lines with 79 width under special conditions
Patch1:         %{name}-docgen.patch

# Add extra check for environment variable if not finding data file
# to avoid make check failure if not already installed
Patch2:         %{name}-cpimport.patch

BuildRequires:  gmp-devel
BuildRequires:  mpfr-devel
BuildRequires:  ntl-devel
BuildRequires:  texlive
BuildRequires:	texlive-collection-pictures

%global sover %(echo %{version} | cut -d. -f 1)


%description
FLINT is a C library for doing number theory, written by William Hart
and David Harvey.


%package        devel
Summary:        Development files for FLINT
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       gmp-devel%{?_isa}
Requires:       mpfr-devel%{?_isa}


%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%prep
%if %{with_snapshot}
%setup -q -n flint2-%{commit}
%else
%setup -q
%endif

%patch0
%patch1
%patch2

# sanitize header files
ln -sf $PWD flint
sed -e 's@\(#[[:space:]]*include\)[[:space:]*]"\([^"]*\)"@\1 <flint/\2>@' \
    -i  `find . -name \*.c -o -name \*.h`
# revert some buggy ones
sed -e 's|#include <mpir.h>|#include <gmp.h>|' \
    -e 's|#include <flint/gmp.h>|#include <gmp.h>|' \
    -e 's|#include <flint/mpir.h>|#include <gmp.h>|' \
    -e 's|#include <flint/mpfr.h>|#include <mpfr.h>|' \
    -e 's|#include <flint/math.h>|#include <math.h>|' \
    -e 's|#include <flint/stdlib.h>|#include <stdlib.h>|' \
    -i  `find . -name \*.c -o -name \*.h`

%build
mkdir bin
ln -sf %{_bindir}/ld.bfd bin/ld
export PATH=$PWD/bin:$PATH

OS=Linux \
MACHINE=%{_arch} \
FLINT_LIB=libflint.so.%{sover} \
sh -x ./configure \
    --prefix=%{_prefix} \
    --libdir=%{_libdir} \
    --with-gmp=%{_libdir} \
    --with-mpfr=%{_libdir} \
    --with-ntl=%{_libdir} \
    --disable-static \
    CFLAGS="%{optflags} -fuse-ld=bfd"
make %{?_smp_mflags}

# Build the documentation
pushd doc/latex
    make manual
popd

%install
make DESTDIR=%{buildroot} install

pushd %{buildroot}%{_libdir}
  ln -s libflint.so.%{sover} libflint.so
popd


%check
export PATH=$PWD/bin:$PATH
make check FLINT_CPIMPORT=$PWD/qadic/CPimport.txt


%files
%doc AUTHORS NEWS README gpl-2.0.txt
%{_libdir}/libflint.so.%{sover}
%{_datadir}/flint


%files devel
%doc INSTALL doc/latex/%{name}-manual.pdf
%{_includedir}/flint
%{_libdir}/libflint.so


%files static
%{_libdir}/libflint.a
