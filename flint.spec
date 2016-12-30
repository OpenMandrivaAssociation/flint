# hmod_mat addon checkout information; this is used by eclib
%global hm_user fredrik-johansson
%global hm_name hmod_mat
%global hm_commit 75378f4af0f0b558385a8bf28d6b4b8ca5f0f568
%global hm_shortcommit %(c=%{hm_commit}; echo ${c:0:7})
%global hm_date 20140328

%define _disable_lto 1

Name:           flint
Version:        2.5.2
Release:        1
Summary:        Fast Library for Number Theory
License:        GPLv2+
URL:            http://www.flintlib.org/
Source0:        http://www.flintlib.org/%{name}-%{version}.tar.gz
Source1:        https://github.com/%{hm_user}/%{hm_name}/archive/%{hm_commit}/%{hm_name}-%{hm_shortcommit}.tar.gz
Source100:	%{name}.rpmlintrc
# Make the hmod_mat extension use gmp instead of mpir
Patch0:         %{name}-hmod_mat.patch
# Bug fixes from upstream git
Patch1:         %{name}-2.5.2-bugfix.patch
# Fix an endless loop with 80-bit floating point on i386
Patch2:         %{name}-float.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1270271
Patch3:         %{name}-gcc5.patch
# Use the popcnt instruction when available
Patch4:         %{name}-popcnt.patch

BuildRequires:  libatlas-devel
BuildRequires:  gc-devel
BuildRequires:  gcc-c++
BuildRequires:  gmp-devel
BuildRequires:  mpfr-devel
BuildRequires:  ntl-devel
BuildRequires:	texlive
BuildRequires:	texlive-collection-pictures


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


%package        static
Summary:        Static libraries for FLINT
Requires:       %{name}-devel%{?_isa} = %{version}-%{release}


%description    static
The %{name}-static package contains static libraries for
developing applications that use %{name}.


%prep
%setup -q -c
%setup -q -T -D -a 1

# Use gmp instead of mpir with hmod_mat
for fil in $(grep -Frl mpir.h hmod_mat-%{hm_commit}); do
  sed -i.orig 's/mpir\.h/gmp.h/' $fil
  touch -r $fil.orig $fil
  rm -f $fil.orig
done

mv hmod_mat-%{hm_commit} %{name}-%{version}/hmod_mat
pushd %{name}-%{version}

%patch0
%patch1 -p1
%patch2
%patch3
%patch4

# TEMPORARY WORKAROUND for bz 1387355.  Remove this once that bug is fixed.
sed -i 's/ \\dots$/ \\ldots/' fmpz_poly/doc/fmpz_poly.txt

# Do not use rpaths
sed -i 's/ -Wl,-rpath,[^"]*\("\)/\1/' configure

# Use ATLAS (which is available on all architectures) instead of openblas
sed -i 's/openblas/satlas/' configure

# Fix test compilation with ATLAS
sed -i 's/$(LIBS)/$(LDFLAGS) &/g' Makefile.in Makefile.subdirs

fixtimestamp() {
  touch -r $1.orig $1
  rm -f $1.orig
}

# sanitize header files
ln -sf $PWD flint
# sanitize references to external headers
for fil in $(find . -name \*.c -o -name \*.h -o -name \*.in); do
  sed -ri.orig 's/"((gc|getopt|gmp|limits|math|stdlib)\.h)"/<\1>/' $fil
  fixtimestamp $fil
done
# sanitize references to flintxx headers
sed_expr=$(ls -1 flintxx/*.h | \
  sed -r 's,flintxx/(.*)\.h,\1,' | \
  awk '/START/{if (x) print x;x="";next}{x=(!x)?$0:x"|"$0;}END{print x;}')
for fil in $(find . -name \*.c -o -name \*.h); do
  sed -ri.orig "s@\"(flintxx/)?(($sed_expr)\.h)\"@<flint/flintxx/\2>@" $fil
  fixtimestamp $fil
done
# sanitize references to all other headers
for fil in $(find . -name \*.c -o -name \*.h); do
  sed -ri.orig 's@"(\.\./)?([^"]+\.h])"@<flint/\2>@' $fil
  fixtimestamp $fil
done
# "
popd

# Prepare to build two versions of the library
cp -a %{name}-%{version} %{name}-%{version}-gc
for fil in $(grep -Frl libflint %{name}-%{version}-gc); do
  sed -i 's/libflint/libflint-gc/' $fil
done


%build
# We set HAVE_FAST_COMPILER to 0 on ARM and s390 because otherwise the tests
# exhaust virtual memory.  If other architectures run out of virtual memory
# while building flintxx/test/t-fmpzxx.cpp, then do likewise.

# Build the non-gc version
pushd %{name}-%{version}
OS=Linux \
MACHINE=%{_arch} \
sh -x ./configure \
    --prefix=%{_prefix} \
    --with-gmp=%{_prefix} \
    --with-mpfr=%{_prefix} \
    --with-blas=%{_includedir}/atlas \
    --with-ntl=%{_prefix} \
    --enable-cxx \
    --extensions=$PWD/hmod_mat \
%ifarch %{arm} s390 %{mips32}
    CFLAGS="%{optflags} -D_FILE_OFFSET_BITS=64 -DHAVE_FAST_COMPILER=0" \
    CXXFLAGS="%{optflags} -D_FILE_OFFSET_BITS=64 -DHAVE_FAST_COMPILER=0"
%else
    CFLAGS="%{optflags} -D_FILE_OFFSET_BITS=64" \
    CXXFLAGS="%{optflags} -D_FILE_OFFSET_BITS=64"
%endif
# FIXME: %%{?_smp_mflags} sometimes fails
make verbose LDFLAGS="-Wl,--as-needed $RPM_LD_FLAGS -L%{_libdir}/atlas" \
  LIBDIR=%{_lib}

# Build the documentation
ln -sf . doc/latex/flint
make -C doc/latex manual CFLAGS="%{optflags} -I$PWD/doc/latex"
popd

# Build the gc version
pushd %{name}-%{version}-gc
OS=Linux \
MACHINE=%{_arch} \
sh -x ./configure \
    --prefix=%{_prefix} \
    --with-gmp=%{_prefix} \
    --with-mpfr=%{_prefix} \
    --with-blas=%{_includedir}/atlas \
    --with-ntl=%{_prefix} \
    --with-gc=%{_prefix} \
    --enable-cxx \
%ifarch %{arm} s390 %{mips32}
    CFLAGS="%{optflags} -D_FILE_OFFSET_BITS=64 -DHAVE_FAST_COMPILER=0" \
    CXXFLAGS="%{optflags} -D_FILE_OFFSET_BITS=64 -DHAVE_FAST_COMPILER=0"
%else
    CFLAGS="%{optflags} -D_FILE_OFFSET_BITS=64" \
    CXXFLAGS="%{optflags} -D_FILE_OFFSET_BITS=64"
%endif
# FIXME: %%{?_smp_mflags} sometimes fails
make verbose LDFLAGS="-Wl,--as-needed $RPM_LD_FLAGS -L%{_libdir}/atlas" \
  LIBDIR=%{_lib}
popd


%install
# Install the gc version
pushd %{name}-%{version}-gc
make install DESTDIR=%{buildroot} LIBDIR=%{_lib}
popd

# Install the non-gc version
pushd %{name}-%{version}
make install DESTDIR=%{buildroot} LIBDIR=%{_lib}

# Fix permissions
chmod 0755 %{buildroot}%{_libdir}/libflint*.so.*

# Install CPimport.txt
mkdir -p %{buildroot}%{_datadir}/flint
cp -p qadic/CPimport.txt %{buildroot}%{_datadir}/flint
popd


%check
pushd %{name}-%{version}
make check QUIET_CC= QUIET_CXX= QUIET_AR= \
  LDFLAGS="-Wl,--as-needed $RPM_LD_FLAGS -L%{_libdir}/atlas" LIBDIR=%{_lib}
popd

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files
%doc %{name}-%{version}/AUTHORS
%doc %{name}-%{version}/NEWS
%doc %{name}-%{version}/README
%doc %{name}-%{version}/gpl-2.0.txt
%{_libdir}/libflint.so.13*
%{_libdir}/libflint-gc.so.13*
%{_datadir}/flint


%files devel
%doc %{name}-%{version}/doc/latex/%{name}-manual.pdf
%{_includedir}/flint/
%{_libdir}/libflint.so
%{_libdir}/libflint-gc.so


%files static
%{_libdir}/libflint.a
%{_libdir}/libflint-gc.a


%changelog
* Thu Oct 20 2016 Jerry James <loganjerry@gmail.com> - 2.5.2-13
- Rebuild for ntl 10.1.0

* Wed Aug 31 2016 Jerry James <loganjerry@gmail.com> - 2.5.2-12
- Rebuild for ntl 9.11.0

* Thu Aug 11 2016 Michal Toman <mtoman@fedoraproject.org> - 2.5.2-11
- HAVE_FAST_COMPILER=0 on 32-bit MIPS (bz 1366672)

* Mon Jul 25 2016 Jerry James <loganjerry@gmail.com> - 2.5.2-10
- Rebuild for ntl 9.10.0

* Thu Jun  2 2016 Jerry James <loganjerry@gmail.com> - 2.5.2-9
- Rebuild for ntl 9.9.1

* Fri Apr 29 2016 Jerry James <loganjerry@gmail.com> - 2.5.2-8
- Rebuild for ntl 9.8.0

* Fri Mar 18 2016 Jerry James <loganjerry@gmail.com> - 2.5.2-7
- Rebuild for ntl 9.7.0

* Sat Feb 20 2016 Jerry James <loganjerry@gmail.com> - 2.5.2-6
- Rebuild for ntl 9.6.4

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.5.2-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Dec  4 2015 Jerry James <loganjerry@gmail.com> - 2.5.2-4
- Rebuild for ntl 9.6.2

* Fri Oct 16 2015 Jerry James <loganjerry@gmail.com> - 2.5.2-3
- Rebuild for ntl 9.4.0

* Sat Oct 10 2015 pcpa <paulo.cesar.pereira.de.andrade@gmail.com> - 2.5.2-2
- Correct detection of gcc 5 as a fast compiler (#1270271)

* Sat Sep 19 2015 Jerry James <loganjerry@gmail.com> - 2.5.2-1
- New upstream release

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.5-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon May 18 2015 Jerry James <loganjerry@gmail.com> - 2.4.5-4
- Rebuild for ntl 9.1.1

* Sat May  9 2015 Jerry James <loganjerry@gmail.com> - 2.4.5-3
- Rebuild for ntl 9.1.0

* Sat May 02 2015 Kalev Lember <kalevlember@gmail.com> - 2.4.5-2
- Rebuilt for GCC 5 C++11 ABI change

* Fri Mar 20 2015 Jerry James <loganjerry@gmail.com> - 2.4.5-1
- New upstream release

* Mon Feb  2 2015 Jerry James <loganjerry@gmail.com> - 2.4.4-6
- Rebuild for ntl 8.1.2

* Mon Jan 12 2015 Jerry James <loganjerry@gmail.com> - 2.4.4-5
- Rebuild for ntl 8.1.0

* Mon Sep 22 2014 Jerry James <loganjerry@gmail.com> - 2.4.4-4
- Rebuild for ntl 6.2.1
- Fix license handling

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Mon Jul 28 2014 Jakub Čajka <jcajka@redhat.com> - 2.4.4-2
- Disable tests that exhaust memory on s390 (bz 1123757)

* Mon Jul 21 2014 Jerry James <loganjerry@gmail.com> - 2.4.4-1
- New upstream release

* Wed Jul 16 2014 Yaakov Selkowitz <yselkowi@redhat.com> - 2.4.2-4
- Fix FTBFS with GMP 6.0 (#1107245)

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed Apr  2 2014 Jerry James <loganjerry@gmail.com> - 2.4.2-2
- Rebuild for ntl 6.1.0
- The -devel subpackage requires ntl-devel

* Mon Mar 17 2014 Jerry James <loganjerry@gmail.com> - 2.4.2-1
- New upstream release

* Mon Feb 10 2014 Jerry James <loganjerry@gmail.com> - 2.4.1-1
- New upstream release
- Enable C++ interface
- Tests now work on 32-bit systems
- Minimize the set of LaTeX BRs
- Enable verbose build
- Link with Fedora LDFLAGS
- On ARM arches, disable tests that exhaust virtual memory while compiling
- Add -fno-strict-aliasing to the test program builds, due to violations of
  the strict aliasing rules in some of the C++ tests

* Mon Aug  5 2013 pcpa <paulo.cesar.pereira.de.andrade@gmail.com> - 2.3-1.20130801git4b383e2
- Update to pre 2.4 snapshot that supports gmp, required by sagemath 5.10

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> 
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon May  6 2013 Jerry James <loganjerry@gmail.com> - 1.6-7
- Rebuild for ntl 6.0.0

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sun Jul 1 2012 pcpa <paulo.cesar.pereira.de.andrade@gmail.com> - 1.6-4
- Build with ntl support to have all symbols resolved.
- Force -fPIC in CFLAGS to avoid ntl link failures.

* Mon May  7 2012 Jerry James <loganjerry@gmail.com> - 1.6-3
- Update warning patch to fix bz 819333

* Mon Jan  9 2012 Jerry James <loganjerry@gmail.com> - 1.6-2
- Rebuild for GCC 4.7

* Thu Oct 20 2011 Marcela Mašláňová <mmaslano@redhat.com> - 1.6-1.2
- rebuild with new gmp without compat lib

* Mon Oct 10 2011 Peter Schiffer <pschiffe@redhat.com> - 1.6-1.1
- rebuild with new gmp

* Mon Jul 18 2011 Jerry James <loganjerry@gmail.com> - 1.6-1
- New upstream release
- Build against the system zn_poly instead of the included sources
- Make sure there is no PIC code in the static archive
- Link mpQS against the shared library instead of including the library
- Fix build errors and scary warnings with gcc 4.6
- Remove unnecessary spec file elements (BuildRoot, etc.)

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sat Jun 26 2010 Thomas Spura <tomspur@fedoraproject.org> - 1.5.2-1
- update to new version
- renew both patches

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Mar 10 2009 Conrad Meyer <konrad@tylerc.org> - 1.2.0-1
- Bump to 1.2.0.

* Fri Mar 6 2009 Conrad Meyer <konrad@tylerc.org> - 1.0.21-1
- Bump to 1.0.21.
- Build static subpackage.

* Sat Dec 6 2008 Conrad Meyer <konrad@tylerc.org> - 1.0.18-1
- Bump to 1.0.18.
- Patches apply with --fuzz=0.

* Sat Nov 29 2008 Conrad Meyer <konrad@tylerc.org> - 1.0.17-1
- Initial package.

