%global with_snapshot 0

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
Version:        2.4.2
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
Requires:       ntl-devel%{?_isa}


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

fixtimestamp() {
  touch -r $1.orig $1
  rm -f $1.orig
}

# sanitize header files
ln -sf $PWD flint
for fil in $(find flintxx -name \*.c -o -name \*.h); do
  sed -e 's@"flint\.h"@<flint/flint.h>@' \
      -e 's@"\(flintxx/[^"]*\)"@<\1>@' \
      -e 's@\(#[[:space:]]*include\)[[:space:]]*"../\([^"]*\)"@\1 <flint/\2>@' \
      -e 's@\(#[[:space:]]*include\)[[:space:]]*"\([^"]*\)"@\1 <flint/flintxx/\2>@' \
      -i.orig $fil
  fixtimestamp $fil
done
for fil in $(find . -name \*.c -o -name \*.h); do
  sed -e 's/\\\?"gmp\.h\\\?"/<gmp.h>/' \
      -e 's/"gc\.h"/<gc.h>/' \
      -e 's/"limits\.h"/<limits.h>/' \
      -e 's/"math\.h"/<math.h>/' \
      -e 's/"stdlib\.h"/<stdlib.h>/' \
      -e 's@\(#[[:space:]]*include\)[[:space:]*]"\([^"]*\)"@\1 <flint/\2>@' \
      -i.orig $fil
  fixtimestamp $fil
done

%build
mkdir bin
ln -sf %{_bindir}/ld.bfd bin/ld
export PATH=$PWD/bin:$PATH

# We set HAVE_FAST_COMPILER to 0 on ARM because otherwise the tests exhaust
# virtual memory.  If other architectures run out of virtual memory while
# building flintxx/test/t-fmpzxx.cpp, then do likewise.
OS=Linux \
MACHINE=%{_arch} \
FLINT_LIB=libflint.so.%{sover} \
sh -x ./configure \
    --prefix=%{_prefix} \
    --libdir=%{_libdir} \
    --with-gmp=%{_libdir} \
    --with-mpfr=%{_libdir} \
    --with-ntl=%{_libdir} \
    --enable-cxx \
%ifarch %{arm}
    CFLAGS="%{optflags} -DHAVE_FAST_COMPILER=0 -fuse-ld=bfd" \
    CXXFLAGS="%{optflags} -DHAVE_FAST_COMPILER=0 -fuse-ld=bfd" \
%else
    CFLAGS="%{optflags}" \
    CXXFLAGS="%{optflags}" \
%endif
    LDFLAGS="-Wl,--as-needed $RPM_LD_FLAGS"
make %{?_smp_mflags} verbose

# Build the documentation
ln -sf . doc/latex/flint
make -C doc/latex manual CFLAGS="%{optflags} -I$PWD/doc/latex"

%install
make DESTDIR=%{buildroot} install

ln -s libflint.so.%{sover} %{buildroot}%{_libdir}/libflint.so

rm %{buildroot}%{_libdir}/libflint.a

%check
# Some of the C++ tests violate the alias analysis rules; i.e., pointers of
# different types point to the same object.  This leads to bad code being
# generated on some platforms, causing the tests to fail.  The actual flint
# code is fine.  This is an artifact of the tests only, so don't pessimize
# the flint build.
sed -ri 's/C(XX)?FLAGS=.*/& -fno-strict-aliasing/' Makefile

make check QUIET_CC= QUIET_CXX= QUIET_AR= CFLAGS="-L%{buildroot}%{_libdir} -lflint %{optflags}"

%files
%doc AUTHORS NEWS README gpl-2.0.txt
%{_libdir}/libflint.so.%{sover}
%{_datadir}/flint


%files devel
%doc doc/latex/%{name}-manual.pdf
%{_includedir}/flint
%{_libdir}/libflint.so
